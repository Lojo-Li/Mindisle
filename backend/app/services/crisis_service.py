"""
危机预防与干预服务
识别用户输入中的危机关键词，自动触发干预机制并优先展示心理援助热线
"""
import re
from typing import List, Optional, Tuple


# ── 危机关键词库（按严重程度分级） ──────────────────────────────────────────

# 一级：极高风险 —— 明确的自我伤害/自杀意图
CRISIS_LEVEL_1_KEYWORDS = [
    "自杀", "自尽", "自刎", "轻生", "跳楼", "跳河", "跳海", "跳江",
    "割腕", "服毒", "上吊", "投河", "投井", "卧轨", "撞车",
    "自我了断", "了结自己", "结束生命", "结束自己",
    "不想活了", "活不下去了", "活够", "不想活",
    "去死", "求死", "找死", "等死",
]

# 二级：高风险 —— 自伤 / 严重心理痛苦
CRISIS_LEVEL_2_KEYWORDS = [
    "自残", "自伤", "自我伤害", "伤害自己", "伤害我",
    "撑不下去", "坚持不住", "熬不下去", "受不了",
    "没希望", "没用", "没有意义", "毫无意义", "一无所有",
    "绝望", "崩溃", "撑不住了", "扛不住",
]

# 三级：中风险 —— 需要关注的心理痛苦表达
CRISIS_LEVEL_3_KEYWORDS = [
    "想死", "死了算", "死掉", "死了好",
    "痛不欲生", "生不如死", "生无可恋",
    "看不到希望", "没有希望", "一片黑暗",
    "解脱", "释放", "逃离", "消失",
]

# 所有关键词合并（用于快速检测）
ALL_CRISIS_KEYWORDS = (
    CRISIS_LEVEL_1_KEYWORDS
    + CRISIS_LEVEL_2_KEYWORDS
    + CRISIS_LEVEL_3_KEYWORDS
)

# ── 心理援助热线 ──────────────────────────────────────────────────────────

CRISIS_HOTLINES = [
    {
        "name": "全国心理援助热线",
        "number": "400-161-9995",
        "description": "24小时免费心理危机干预",
    },
    {
        "name": "希望24热线",
        "number": "400-161-9995",
        "description": "全国24小时心理危机干预热线",
    },
    {
        "name": "北京心理危机研究与干预中心",
        "number": "010-82951332",
        "description": "24小时免费心理危机干预",
    },
    {
        "name": "全国24小时免费心理援助热线",
        "number": "12320",
        "description": "公共卫生服务热线（转心理援助）",
    },
]

# ── 危机干预信息模板 ──────────────────────────────────────────────────────

CRISIS_INTERVENTION_TEMPLATE = """【💚 请先停下来，看看这些重要信息】

我注意到你可能正在经历非常艰难的时刻。你的感受很重要，请先联系专业的心理援助资源，他们会给你最及时的帮助：

{hotline_list}

🌟 **你并不孤单，请一定拨打上面的电话，有专业人士在等你。**

---

（以下是我的回应，希望能给你一些支持）"""

CRISIS_INTERVENTION_TEMPLATE_SHORT = """💚 你的安全最重要！请立即拨打 **全国心理援助热线：400-161-9995**（24小时免费），有专业心理咨询师在等你。"""


def detect_crisis(text: str) -> Tuple[int, List[str]]:
    """
    检测文本中是否包含危机关键词

    Args:
        text: 用户输入的文本

    Returns:
        Tuple[int, List[str]]:
            - 0 = 无危机，1 = 三级（中风险），2 = 二级（高风险），3 = 一级（极高风险）
            - 匹配到的关键词列表
    """
    if not text or not text.strip():
        return 0, []

    matched_keywords = []

    # 从最高级别开始检查
    for level, keywords in [
        (3, CRISIS_LEVEL_1_KEYWORDS),
        (2, CRISIS_LEVEL_2_KEYWORDS),
        (1, CRISIS_LEVEL_3_KEYWORDS),
    ]:
        for kw in keywords:
            if kw in text:
                matched_keywords.append(kw)

    if not matched_keywords:
        return 0, []

    # 返回实际最高级别
    max_level = 0
    for kw in matched_keywords:
        if kw in CRISIS_LEVEL_1_KEYWORDS:
            max_level = max(max_level, 3)
        elif kw in CRISIS_LEVEL_2_KEYWORDS:
            max_level = max(max_level, 2)
        elif kw in CRISIS_LEVEL_3_KEYWORDS:
            max_level = max(max_level, 1)

    return max_level, matched_keywords


def format_hotline_list() -> str:
    """格式化热线列表文本"""
    lines = []
    for hotline in CRISIS_HOTLINES:
        lines.append(f"- **{hotline['name']}**：{hotline['number']}（{hotline['description']}）")
    return "\n".join(lines)


def build_crisis_intervention_prompt(is_crisis: bool) -> str:
    """构建完整的危机干预提示内容（嵌入到 system prompt 中）"""
    if not is_crisis:
        return ""
    return CRISIS_INTERVENTION_TEMPLATE.format(hotline_list=format_hotline_list())


def build_crisis_system_instruction(is_crisis: bool) -> str:
    """
    当检测到危机时，生成额外的 system prompt 指令

    Args:
        is_crisis: 是否检测到危机

    Returns:
        str: 附加的 system prompt 片段
    """
    if not is_crisis:
        return ""

    hotline_text = format_hotline_list()

    return f"""
【⚠️ 危机干预指令 — 紧急情况】

检测到用户当前消息包含心理危机/自伤倾向信号。你必须：

1. **用户的安全是第一优先级**。但不要一上来就列热线，而是**先充分共情和安抚**用户情绪。
2. **首先倾听和安抚**：用温暖、接纳的语气先回应用户的情感痛苦，让用户感受到被理解和被关心。
3. **逐步、委婉地提供帮助信息**：在建立情感连接之后，用温和的语气提及心理援助热线，避免生硬或机械地罗列。
4. **明确给出以下热线信息**（必须包含，但在充分共情之后再说）：

{hotline_text}

5. 然后根据用户的具体困扰提供温和的心理支持建议。
6. 不得替用户做任何决定。
7. 回复风格：温暖、关怀、坚定、不评判。

【参考回复结构】

1. **先共情**：理解用户的痛苦感受（例如“我能感受到你现在真的很不容易”等）
2. **再安抚**：传递温暖和关心，给予情感支持
3. **最后温和提及资源**：在用户感到被理解后，委婉地告诉用户有热线可以提供帮助

---
{{
    // 此处输出 AI 的心理支持内容
}}
"""


# ── 对外暴露的便捷方法 ──────────────────────────────────────────────────

def is_crisis_detected(text: str) -> bool:
    """快速判断是否包含危机关键词"""
    level, _ = detect_crisis(text)
    return level > 0


def get_crisis_level_label(level: int) -> str:
    """获取危机等级标签"""
    labels = {0: "无", 1: "三级（中风险）", 2: "二级（高风险）", 3: "一级（极高风险）"}
    return labels.get(level, "未知")


def get_crisis_quick_response() -> str:
    """获取简短的危机即时响应文本（可用于流式消息前置）"""
    return CRISIS_INTERVENTION_TEMPLATE_SHORT
