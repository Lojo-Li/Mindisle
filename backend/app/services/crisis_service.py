"""
危机预防与干预服务

职责：
1. 对用户输入做风险分级（L1 关注 / L2 警示 / L3 紧急）
2. 给出该等级应触发的处置动作，供前端与后台执行
3. 生成注入到 system prompt 的干预指令

设计原则（重要）：
- 安全兜底不交给模型。L2/L3 的热线由前端强制渲染，
  不依赖模型是否"记得"输出，prompt 只负责语气与共情。
- 判定结果必须可落库、可追溯，才能复盘与统计。

本模块对旧接口保持向后兼容：
  detect_crisis(text) -> (level, keywords)
  is_crisis_detected / get_crisis_level_label / build_crisis_system_instruction ...
"""
import json
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from app.core.config import settings

# ── 分级关键词库 ────────────────────────────────────────────────────────
# 只收录"指向自身"的表达。像"去死""找死""等死"这类多用于他指或口语，
# 误报率极高，已从词库移除。

# L3 紧急：明确的自伤/自杀意图或方式
LEVEL3_KEYWORDS = [
    "自杀", "自尽", "自刎", "轻生", "紫砂",  # 紫砂为网络谐音
    "割腕", "服毒", "上吊", "投河", "投井", "卧轨", "跳楼", "跳河", "跳海", "跳江",
    "自我了断", "结束生命", "结束自己", "了结自己",
    "不想活了", "活不下去了", "不想活",
]

# L2 警示：自伤意念 / 严重心理痛苦
LEVEL2_KEYWORDS = [
    "自残", "自伤", "自我伤害", "伤害自己", "伤害我自己",
    "想死", "死了算了", "死了算", "死了好", "一死了之",
    "撑不下去", "撑不住了", "熬不下去", "扛不住", "受不了了",
    "绝望", "崩溃", "生不如死", "痛不欲生", "生无可恋",
]

# L1 关注：需要被看见的持续性低落
LEVEL1_KEYWORDS = [
    "没有希望", "看不到希望", "一片黑暗", "毫无意义",
    "活着没意思", "一无所有", "没有意义", "麻木",
]

LEVEL_KEYWORDS = {3: LEVEL3_KEYWORDS, 2: LEVEL2_KEYWORDS, 1: LEVEL1_KEYWORDS}
ALL_CRISIS_KEYWORDS = LEVEL3_KEYWORDS + LEVEL2_KEYWORDS + LEVEL1_KEYWORDS

# 口语中的"死"字用法，匹配前先剥离，避免"笑死我了"被判为风险
FALSE_POSITIVE_PHRASES = [
    "笑死", "累死", "气死", "热死", "冷死", "困死", "吓死", "烦死", "饿死",
    "死机", "死板", "死心眼", "死循环", "死线",
    "去死吧你", "找死啊",
]

# 否定词：出现在关键词前若干字符内，视为否定表达。
# 不含单独的"未"，避免"未来"被误判为否定。
NEGATIONS = ["不", "没", "没有", "别", "从未", "从未有", "未曾", "尚未", "并未", "并不", "不再", "哪有"]

NEGATION_WINDOW = 8

# 否定只在其所在的分句内生效。
# 例："我不开心，不想活了" —— "不"在逗号前，不影响后半句的风险判定；
# 而"我没有不想活"没有标点隔断，属于否定表达。
CLAUSE_SEPARATORS = "，,。.！!？?；;、\n"

# ── 心理援助热线（可在 settings.CRISIS_HOTLINES_JSON 覆盖）──────────────
DEFAULT_HOTLINES = [
    {"name": "全国心理援助热线", "number": "12356", "description": "国家卫健委统一热线，24 小时"},
    {"name": "北京心理危机研究与干预中心", "number": "010-82951332", "description": "24 小时免费危机干预"},
    {"name": "希望24热线", "number": "400-161-9995", "description": "24 小时心理危机干预"},
]


def get_hotlines() -> List[dict]:
    """读取热线配置，失败时回落到内置默认值。"""
    raw = getattr(settings, "CRISIS_HOTLINES_JSON", "") or ""
    if not raw.strip():
        return list(DEFAULT_HOTLINES)
    try:
        data = json.loads(raw)
        if isinstance(data, list) and data:
            return data
    except Exception:
        pass
    return list(DEFAULT_HOTLINES)


# 兼容旧代码里的 CRISIS_HOTLINES 引用
CRISIS_HOTLINES = get_hotlines()

# ── 分级处置动作矩阵 ─────────────────────────────────────────────────────
LEVEL_ACTIONS = {
    0: [],
    1: ["gentle_hint", "self_help_card"],
    2: ["banner", "hotline_card", "appointment_cta", "notify_counselor"],
    3: ["blocking_dialog", "hotline_card", "hotline_call", "human_handover",
        "force_record", "notify_admin"],
}

LEVEL_LABELS = {
    0: "无",
    1: "L1 关注",
    2: "L2 警示",
    3: "L3 紧急",
}


@dataclass
class RiskVerdict:
    """一次风险判定的完整结果。"""
    level: int = 0
    keywords: List[str] = field(default_factory=list)
    negated: List[str] = field(default_factory=list)

    @property
    def is_risk(self) -> bool:
        return self.level > 0

    @property
    def label(self) -> str:
        return LEVEL_LABELS.get(self.level, "未知")

    @property
    def actions(self) -> List[str]:
        return LEVEL_ACTIONS.get(self.level, [])

    @property
    def hotlines(self) -> List[dict]:
        return get_hotlines() if self.level >= 2 else []

    def to_payload(self) -> dict:
        """推给前端的事件体。"""
        return {
            "level": self.level,
            "label": self.label,
            "keywords": self.keywords,
            "actions": self.actions,
            "hotlines": self.hotlines,
        }


def _normalize(text: str) -> str:
    """全角转半角并去空白，避免"自 杀"这类规避写法漏判。"""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).replace(" ", "").replace("\u3000", "")


def _strip_false_positives(text: str) -> str:
    for phrase in FALSE_POSITIVE_PHRASES:
        text = text.replace(phrase, "")
    return text


def _is_negated(text: str, start: int, keyword: str) -> bool:
    """
    判断某个关键词是否处于否定语境。

    只看关键词所在分句内、且位于关键词之前的否定词：
    - "我没有想自杀"     -> 否定成立
    - "我不开心，不想活了" -> 逗号隔断，否定不成立（这条必须判为高危）
    """
    window = text[max(0, start - NEGATION_WINDOW):start]
    for sep in CLAUSE_SEPARATORS:
        if sep in window:
            window = window.rsplit(sep, 1)[-1]
    return any(n in window for n in NEGATIONS)


def detect_risk(text: str) -> RiskVerdict:
    """
    完整风险判定，返回 RiskVerdict。

    与 detect_crisis 的区别：会剔除否定语境与口语误报，
    并携带处置动作，供上层直接使用。
    """
    if not text or not text.strip():
        return RiskVerdict()

    normalized = _strip_false_positives(_normalize(text))

    matched: List[str] = []
    negated: List[str] = []
    max_level = 0

    for level in (3, 2, 1):
        for keyword in LEVEL_KEYWORDS[level]:
            idx = normalized.find(keyword)
            if idx < 0:
                continue
            if _is_negated(normalized, idx, keyword):
                if keyword not in negated:
                    negated.append(keyword)
                continue
            if keyword not in matched:
                matched.append(keyword)
            max_level = max(max_level, level)

    return RiskVerdict(level=max_level, keywords=matched, negated=negated)


# ── 向后兼容接口 ─────────────────────────────────────────────────────────

def detect_crisis(text: str) -> Tuple[int, List[str]]:
    """
    检测文本中的风险等级（兼容旧调用）。

    Returns:
        (level, keywords)
        level: 0 无 / 1 关注 / 2 警示 / 3 紧急
    """
    verdict = detect_risk(text)
    return verdict.level, verdict.keywords


def is_crisis_detected(text: str) -> bool:
    return detect_risk(text).level > 0


def get_crisis_level_label(level: int) -> str:
    return LEVEL_LABELS.get(level, "未知")


def get_crisis_quick_response() -> str:
    """简短即时响应（可用于无模型的兜底场景）。"""
    first = get_hotlines()[0]
    return (
        "你的安全最重要。请立即拨打 "
        f"**{first['name']}：{first['number']}**，"
        "有专业心理咨询师 24 小时在等你。"
    )


def format_hotline_list() -> str:
    lines = []
    for hotline in get_hotlines():
        lines.append(
            f"- **{hotline['name']}**：{hotline['number']}（{hotline.get('description', '')}）"
        )
    return "\n".join(lines)


# ── 注入 system prompt 的干预指令 ────────────────────────────────────────

CRISIS_INTERVENTION_TEMPLATE = """【重要提示】
我注意到你可能正在经历非常艰难的时刻。你的感受很重要，
下面这些电话可以给你更及时的帮助：

{hotline_list}
"""


def build_crisis_intervention_prompt(is_crisis: bool) -> str:
    if not is_crisis:
        return ""
    return CRISIS_INTERVENTION_TEMPLATE.format(hotline_list=format_hotline_list())


def build_crisis_system_instruction(is_crisis: bool, level: int = 0) -> str:
    """
    危机时追加到 system prompt 的指令。

    注意：这里只负责"怎么说"，不承担"必须让用户看到热线"的职责。
    后者由前端按 LEVEL_ACTIONS 强制渲染，避免模型漏输出导致兜底失效。
    """
    if not is_crisis:
        return ""

    if level >= 3:
        stance = (
            "用户可能正处于紧急状态。请用最温和、最直接的方式表达关心，"
            "不要反问、不要讲道理、不要罗列清单。承认 ta 此刻的痛苦，"
            "明确告诉 ta 你希望 ta 现在就联系专业的人。"
        )
    elif level >= 2:
        stance = (
            "用户正在经历强烈的心理痛苦。请先充分共情，让 ta 感到被理解，"
            "再温和地提及可以寻求专业帮助，不要说教、不要急于给方案。"
        )
    else:
        stance = (
            "用户的表达里透出持续的低落。请温和地回应情绪，"
            "可以提议一些轻量的自我照顾方式，不要过度紧张化。"
        )

    return f"""
【安全提示上下文】
{stance}

如需提及求助渠道，可使用以下信息（界面上会同步展示，不必逐条罗列）：
{format_hotline_list()}

边界：不做诊断、不建议药物、不承诺替代专业咨询。
"""


# ── 情绪标签（供统计与趋势使用，不参与风险判定）──────────────────────────

EMOTION_HINTS = {
    "anxiety": ["焦虑", "紧张", "担心", "害怕", "心慌", "不安"],
    "depression": ["低落", "难过", "想哭", "没劲", "提不起", "空虚"],
    "anger": ["生气", "愤怒", "火大", "烦躁", "暴躁"],
    "sleep": ["失眠", "睡不着", "早醒", "多梦"],
    "relation": ["分手", "吵架", "父母", "室友", "同事", "孤独"],
}


def guess_emotion_label(text: str) -> Optional[str]:
    """极简情绪打标，仅用于列表展示与趋势统计。"""
    if not text:
        return None
    hits = {}
    for label, words in EMOTION_HINTS.items():
        count = sum(1 for w in words if w in text)
        if count:
            hits[label] = count
    if not hits:
        return None
    return max(hits.items(), key=lambda kv: kv[1])[0]
