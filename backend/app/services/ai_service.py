"""
AI 服务 - 基于豆包 API
"""
import os
import time
import httpx
from typing import Iterator
from openai import OpenAI
from app.core.config import settings


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端"""
        # 创建httpx客户端，禁用SSL验证以避免Windows上的SSL错误
        http_client = httpx.Client(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
            verify=settings.AI_VERIFY_SSL  # 默认校验证书，见 config.AI_VERIFY_SSL
        )

        self.client = OpenAI(
            base_url=settings.DOUBAO_BASE_URL,
            api_key=settings.DOUBAO_API_KEY,
            http_client=http_client
        )
        self.model = settings.DOUBAO_MODEL

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
                    return completion.choices[0].message.content

            except Exception as e:
                # 如果是最后一次尝试，抛出异常
                if attempt == max_retries - 1:
                    raise Exception(f"AI 服务调用失败（已重试{max_retries}次）: {str(e)}")

                # 等待一段时间后重试
                wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                print(f"AI服务调用失败，{wait_time}秒后进行第{attempt + 2}次重试... 错误: {str(e)}")
                time.sleep(wait_time)

                # 重新创建客户端（连接可能已损坏）
                http_client = httpx.Client(
                    timeout=60.0,
                    limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
                    verify=settings.AI_VERIFY_SSL
                )
                self.client = OpenAI(
                    base_url=settings.DOUBAO_BASE_URL,
                    api_key=settings.DOUBAO_API_KEY,
                    http_client=http_client
                )

    def chat_stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Iterator[str]:
        """发起流式聊天请求，逐块返回文本。"""
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
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"AI 服务流式调用失败: {str(e)}")

    def generate_system_prompt(self, context: str = "") -> str:
        """
        生成系统提示词

        Args:
            context: 上下文信息（可选）

        Returns:
            str: 系统提示词
        """
        assistant_name = getattr(settings, "AI_ASSISTANT_NAME", "小屿")
        base_prompt = f"""你是「心屿 Mindisle」心理支持平台的智能助手，名叫"{assistant_name}"。你的职责是：

1. **专业角色**：你是一个温暖、专业、有同理心的心理健康陪伴者，不是医生
2. **服务宗旨**：为用户提供情绪支持、心理健康知识普及和自助方法建议
3. **交流风格**：
   - 语气温和、友善，不带评判色彩
   - 善于倾听，先回应情绪，再谈方法
   - 使用通俗易懂的语言，避免专业术语堆砌
   - 不空泛安慰，尽量给一个具体、今天就能做的小动作

4. **能力边界（务必遵守）**：
   - **不下诊断**：不说"你得了抑郁症/焦虑症"，只描述状态
   - **不建议药物**：任何药物、剂量、停药问题都建议就医
   - **不替代咨询**：明确说明你是 AI 支持，不能替代专业心理咨询
   - 保持中立，不替用户做决定

5. **回答依据（极其重要）**：
   - 如果下方提供了知识库参考，请吸收后用自己的话表达，可自然地说"心理学上通常会…"
   - 如果**没有**提供知识库参考，不要编造研究、数据、书名或"研究表明"
   - 拿不准时直接说"这一点我不确定，建议和咨询师确认"

6. **危机干预**：
   - 若用户表现出自伤、自杀等危机信号：先充分共情，让对方感到被理解，
     再温和地鼓励其立即联系专业帮助
   - 界面上会同步展示援助热线，你不必机械罗列，重点是把人接住
   - 不要讲道理、不要反问、不要急于给解决方案

7. **回复格式**：
   - **通常不超过 200 字**，除非用户明确要求展开
   - 一次只给 1-2 个要点，避免信息过载
   - 可以用少量表情符号让语气更柔和（如 💚 🌿）
   - 不要用"首先/其次/最后"这种报告式结构"""

        if context:
            return f"""{base_prompt}

**【知识库参考 — 请用温暖口吻转述】**
下方案例供你参考，请吸收核心信息后**用自己的语言**重新表达，
不要让用户感觉在读教科书：

{context}"""
        return base_prompt


# 创建全局 AI 服务实例
ai_service = AIService()
