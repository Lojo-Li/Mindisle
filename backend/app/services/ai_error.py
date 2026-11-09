"""
AI 服务错误的人话转换

为什么需要：模型不可用时，原始报错会被直接写进对话内容，例如
    Error code: 404 - {'error': {'code': 'ModelNotOpen', 'message': ... Request id: ...}}
用户（尤其正处于情绪困扰中的人）看到这串东西，体验是"我说了话，机器坏了"。
这里把技术错误分类，转成可读、可行动的话；技术细节只进日志。
"""

import logging

logger = logging.getLogger(__name__)

# 面向用户的兜底回复：承认故障、给出可行动的下一步、不假装一切正常
FRIENDLY_UNAVAILABLE = (
    "抱歉，屿灯这边暂时有点故障，没能正常回应你。\n"
    "如果你现在状态不太好，可以先联系专业的心理支持：全国心理援助热线 12356（24 小时）。\n"
    "这次故障我已经记录下来了。"
)

FRIENDLY_TIMEOUT = (
    "抱歉，刚才回应得有点慢，没能接上你的话。\n"
    "你可以再说一次，或者换个说法告诉我此刻的感受。"
)


def _code_of(err: Exception) -> str:
    """从异常里尽量抠出服务端的错误码"""
    text = str(err)
    for code in (
        "ModelNotOpen", "InvalidEndpoint", "AuthenticationError", "InvalidApiKey",
        "RateLimitExceeded", "QuotaExceeded", "AccessDenied", "InvalidParameter",
        "content_filter", "sensitive",
    ):
        if code in text:
            return code
    return ""


def friendly_message(err: Exception) -> str:
    """
    把异常转成面向用户的回复，同时把完整信息写日志。
    未识别的错误也返回兜底文案，绝不要把原始报错抛给用户。
    """
    logger.error("[AI] 调用失败: %s", err)
    text = str(err).lower()
    code = _code_of(err)

    if code in ("ModelNotOpen", "InvalidEndpoint", "AccessDenied", "InvalidApiKey", "AuthenticationError"):
        # 配置类问题：用户怎么重试都没用，直接给兜底与求助渠道
        return FRIENDLY_UNAVAILABLE

    if code in ("RateLimitExceeded", "QuotaExceeded"):
        return (
            "抱歉，屿灯现在有点忙，暂时回应不了你。\n"
            "你可以过几分钟再试，或者先联系专业的心理支持：全国心理援助热线 12356。"
        )

    if "timeout" in text or "timed out" in text:
        return FRIENDLY_TIMEOUT

    return FRIENDLY_UNAVAILABLE
