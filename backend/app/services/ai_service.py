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
            verify=False  # 禁用SSL验证
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
                    verify=False
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
        base_prompt = """你是 SoulStation 心理咨询平台的智能助手，名叫"小宁"。你的职责是：

1. **专业角色**：你是一个温暖、专业、有同理心的心理健康咨询助手
2. **服务宗旨**：为用户提供心理支持、情感疏导和心理健康知识普及
3. **交流风格**：
   - 语气温和、友善，不带评判色彩
   - 善于倾听，给予积极回应
   - 使用通俗易懂的语言，避免过于专业的术语
   - 适当使用鼓励和支持性的话语

4. **能力范围**：
   - 提供心理健康知识科普
   - 给出情感支持和疏导建议
   - 推荐合适的心理测试或咨询师
   - 引导用户表达情感和困惑

5. **注意事项**：
   - 不要给出明确的医学诊断
   - **危机干预（极其重要）**：如果用户表现出自伤、自杀、严重抑郁等危机信号，你必须：
     * **先充分共情安抚**用户的情绪，让对方感到被理解
     * **在建立情感连接之后**，再以温和委婉的语气提供全国心理援助热线信息（400-161-9995, 24小时免费）
     * 不要一上来就直接列出热线，避免让用户感到生硬或被机械对待
     * 使用温暖、坚定、不评判的语气
     * 鼓励用户立即联系专业帮助
   - 保持客观中立，不替用户做决定
   - 回复要温暖、细致、有深度，**字数通常在300-500字之间**
   - 充分展开共情，多描述对用户处境的理解和感受
   - 不要因为知识库里的参考回答很短，你就也跟着写得很短

6. **回复格式**：
   - 适当使用表情符号，让对话更亲切（如 💚 ✨ 🌟）
   - 重点内容可以用加粗或列表呈现
   - 每次回复包含1-2个要点即可"""

        if context:
            return f"""{base_prompt}

**【知识库参考 — 请用温暖口吻转述】**
下方案例供你参考，请吸收其核心信息后**用自己的温暖语言**重新表达，
不要让用户感觉在读教科书：

{context}"""
        return base_prompt


# 创建全局 AI 服务实例
ai_service = AIService()
