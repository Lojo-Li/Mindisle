"""
AI 服务 - 基于豆包 API
"""
import os
import time
import httpx
from typing import Iterator, Optional
from openai import OpenAI
from app.core.config import settings
from app.services import llm_config


# ---- 熔断状态 ----
# 说明：豆包侧若返回 4xx（如 InvalidEndpoint.ClosedEndpoint 表示模型端点已下线），
# 重试没有任何意义，反而会在 async 接口里用 time.sleep 阻塞整个事件循环，
# 表现就是"所有接口一起超时、前端提示网络未连接"。这里做两件事：
#   1) 4xx 不重试，立即失败；
#   2) 连续失败达到阈值后熔断一段时间，期间直接跳过 AI，不再发起网络请求。
_FAIL_STREAK = 0
_OPEN_UNTIL = 0.0
_FAIL_THRESHOLD = 2
_OPEN_SECONDS = 300  # 熔断 5 分钟

# 这些状态码属于"调用方式/凭证/端点"问题，重试无意义
_NON_RETRYABLE_STATUS = {400, 401, 403, 404, 422}


def _status_of(exc: Exception):
    """尽力从异常里取出 HTTP 状态码"""
    resp = getattr(exc, "response", None)
    code = getattr(resp, "status_code", None)
    if isinstance(code, int):
        return code
    text = str(exc)
    for c in _NON_RETRYABLE_STATUS:
        if f"Error code: {c}" in text:
            return c
    return None


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端（配置可变，见 _ensure_client）"""
        self.client: Optional[OpenAI] = None
        self.model: str = ""
        self._signature = None
        self._http_client: Optional[httpx.Client] = None
        self._ensure_client()

    # ── 配置热加载 ────────────────────────────────────────────────
    def _build_client(self, cfg: llm_config.LLMConfig) -> None:
        """按给定配置重建客户端；旧的连接池顺手关掉，避免句柄泄漏。"""
        try:
            if self._http_client is not None:
                self._http_client.close()
        except Exception:
            pass

        # 超时收紧：连接 8s、读 30s。
        self._http_client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=8.0),
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
            verify=settings.AI_VERIFY_SSL  # 默认校验证书，见 config.AI_VERIFY_SSL
        )
        self.client = OpenAI(
            base_url=cfg.base_url,
            api_key=cfg.api_key,
            http_client=self._http_client
        )
        self.model = cfg.model

    def _ensure_client(self) -> llm_config.LLMConfig:
        """每次调用前确认配置未变；变了就重建客户端并清掉熔断状态。

        这样换 key 只需要改 llm.json（或环境变量后重启），不需要动代码，
        也不会出现"换了 key 还被上一次的失败锁在熔断期里"的情况。
        """
        global _FAIL_STREAK, _OPEN_UNTIL

        cfg = llm_config.load()
        if self.client is not None and cfg.signature == self._signature:
            return cfg

        changed = self._signature is not None
        self._build_client(cfg)
        self._signature = cfg.signature

        if changed:
            _FAIL_STREAK = 0
            _OPEN_UNTIL = 0.0
            print(f"[AI] 配置已切换 → {cfg.source} / {cfg.model} / {cfg.masked_key}")
        return cfg

    @staticmethod
    def circuit_open() -> bool:
        """熔断中：直接跳过 AI 调用，避免拖慢主流程"""
        return time.time() < _OPEN_UNTIL

    def chat(
        self,
        messages: list,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
    ) -> str:
        """
        发起聊天请求（带重试机制）

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            stream: 是否流式返回
            temperature: 温度参数（0-1），越高越随机
            max_tokens: 最大 token 数
            max_retries: 最大重试次数

        Returns:
            str: AI 的回复内容
        """
        global _FAIL_STREAK, _OPEN_UNTIL

        # 先确认配置是否有变化（换 key 会顺带清掉熔断）
        self._ensure_client()

        # 熔断中：不再发起网络请求，立刻返回错误。
        # 这样即使端点不可用，主流程（提交测评）也不会被拖住。
        if self.circuit_open():
            raise Exception("AI 服务暂不可用（已熔断，稍后自动恢复）")

        for attempt in range(max_retries):
            try:
                if stream:
                    # 流式返回
                    response = ""
                    stream_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        stream=True,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            response += chunk.choices[0].delta.content
                    _FAIL_STREAK = 0
                    return response
                else:
                    # 非流式返回
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        stream=False,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    _FAIL_STREAK = 0
                    return completion.choices[0].message.content

            except Exception as e:
                status = _status_of(e)
                _FAIL_STREAK += 1

                # 连续失败达到阈值 → 熔断，后续调用直接跳过
                if _FAIL_STREAK >= _FAIL_THRESHOLD:
                    _OPEN_UNTIL = time.time() + _OPEN_SECONDS
                    print(f"[AI] 连续失败 {_FAIL_STREAK} 次，熔断 {_OPEN_SECONDS}s：{e}")

                # 4xx（端点关闭/鉴权/参数错误）重试无意义，直接抛出
                if status in _NON_RETRYABLE_STATUS:
                    raise Exception(f"AI 服务不可用（HTTP {status}）: {e}")

                # 如果是最后一次尝试，抛出异常
                if attempt == max_retries - 1:
                    raise Exception(f"AI 服务调用失败（已重试{max_retries}次）: {str(e)}")

                # 等待一段时间后重试
                wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                print(f"AI服务调用失败，{wait_time}秒后进行第{attempt + 2}次重试... 错误: {str(e)}")
                time.sleep(wait_time)

                # 重新创建客户端（连接可能已损坏）
                self._build_client(llm_config.load())

    def chat_stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 2,
    ) -> Iterator[str]:
        """发起流式聊天请求，逐块返回文本。

        网关偶尔会直接掐断连接（Windows 上表现为 WinError 10054）。只要还没
        往前端吐过任何字符，重试就是安全的；一旦已经吐过就不再重试，否则用户
        会看到重复的半句话。
        """
        self._ensure_client()

        for attempt in range(max_retries):
            emitted = False
            try:
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                for chunk in stream_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        emitted = True
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                if emitted or attempt == max_retries - 1:
                    raise Exception(f"AI 服务流式调用失败: {str(e)}")
                wait = attempt + 1
                print(f"[AI] 流式中断，{wait}s 后重试（第 {attempt + 2} 次）：{e}")
                time.sleep(wait)
                self._build_client(llm_config.load())

    def generate_system_prompt(self, context: str = "") -> str:
        """
        生成系统提示词

        Args:
            context: 上下文信息（可选）

        Returns:
            str: 系统提示词
        """
        assistant_name = getattr(settings, "AI_ASSISTANT_NAME", "小屿")
        base_prompt = f"""你是「心屿 Mindisle」心理支持平台的陪伴助手，名叫"{assistant_name}"。

【你是谁】
不是客服，也不是老师。你像一个凌晨两点还醒着、愿意听人说话的朋友。
懂一点心理学，但不把术语挂在嘴上。

【怎么说话】
- 像发微信，不像写文章。多用短句，允许"嗯""其实""我猜"这类口语。
- 先用一句话接住对方的情绪，让对方知道"你听懂了"，再往下说。
- 不要说"首先/其次/最后"，不要用列表、编号、加粗、小标题。
- 不空泛安慰（"一切都会好起来的"），也不喊口号。
- 可以用 1 个 emoji，不要每段都放。

【一次回答的骨架】
1. 先回应情绪：具体说出你听到的那种感受，而不是"我理解你"。
2. 再落一个具体的点：对方话里最值得展开的那一句。
3. 给一件今天就能做的小事：具体到动作（"睡前把手机放到客厅充电"），
   不要说"你要放松""调整心态"。
4. 结尾可以留一句轻轻的邀请（"要不要说说，是从什么时候开始的？"），
   但不要每句都追问。

【篇幅】
- 有知识库参考时：250-400 字，把参考里的信息消化掉再说，不要照抄。
- 没有参考时：150-250 字，宁可短一点，也不要用废话填满。

【边界】
- 不做诊断：不说"你有抑郁症/焦虑症"，只描述状态。
- 不谈药物、剂量、停药，一律建议就医。
- 不说"我能治好你"，明确你是 AI 陪伴，不替代专业咨询。
- 不替对方做决定（分手、辞职这类），只帮他把选项摆清楚。

【关于依据】
- 有参考：自然转述，"心理学里有一种说法是…"，不要出现"根据文档第几条"。
- 没有参考：可以说"这点我没有直接资料"，但仍然要给出通用的、无害的建议，
  不要因为怕出错就只说空话。绝不能编造研究、数据、书名。

【危机情况】
对方若表现出自伤、自杀、伤害他人的念头：
- 先共情，明确说出你的担心（"我听到这句话有点担心你"），不要追问细节、不要讲道理。
- 鼓励他立刻联系专业帮助，界面上会同步显示热线，你不必机械罗列号码。
- 不要试图"劝回来"，也不要承诺"你会没事的"。"""

        if context:
            return f"""{base_prompt}

【这次可参考的知识库片段】
下面是从知识库检索到的真实案例/条目。请吸收后用自己的话讲出来，
让用户觉得是"有人在跟他说"，而不是在读教科书：

{context}"""
        return base_prompt


# 创建全局 AI 服务实例
ai_service = AIService()
