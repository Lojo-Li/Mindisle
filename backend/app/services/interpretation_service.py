"""
结果解释服务（Interpretation）

职责：把「一个分数」翻译成人能读懂的解读，并且保证这件事是**确定性、可追溯**的：
1. 等级判定来自量表自己的 result_rules.levels，不是写死在代码里的 if/else；
2. 每条解读都说明依据（命中哪一档、区间多少、维度怎么算出来的）；
3. 不调用大模型也能给出完整解释，AI 建议只作为补充而不是支柱。

输出结构（前端 TestResult 直接消费）：
{
  "version": "interp-v1",
  "level": {code,label,range,position,summary,signs},
  "dimensions": [{name,score,max_score,percent,band,note}],
  "advice": {today:[],week:[],professional:[]},
  "signal": {level,tone,title,text},
  "disclaimer": str,
  "trace": {thresholds:[{code,label,min,max,matched}], score_basis:{...}, notes:[]}
}
"""
from typing import Any, Dict, List, Optional


# ---------------- 等级文案库 ----------------
# 键为等级 code，覆盖各量表常见的 four-level 命名；找不到时走 _fallback_level
LEVEL_COPY: Dict[str, Dict[str, Any]] = {
    "none": {
        "label": "状态平稳",
        "summary": "当前的得分落在最低区间，没有明显的困扰信号。",
        "signs": ["情绪大体稳定，日常功能未受影响", "睡眠、食欲基本正常"],
        "today": ["保持现有的作息节奏，不必额外加码", "记录一件今天让你放松的小事"],
        "week": ["保持每周 3 次以上、每次 20 分钟的活动量", "给自己留一段不被打扰的独处时间"],
        "professional": [],
        "tone": "routine",
    },
    "mild": {
        "label": "轻度",
        "summary": "出现了一些轻微信号，还在可自我调节的范围内。",
        "signs": ["偶尔紧张、烦躁或提不起劲", "注意力比平时略难集中", "入睡比以前慢一些"],
        "today": ["做 3 分钟缓慢呼吸：吸 4 秒、停 2 秒、呼 6 秒", "把今天最要紧的一件事写下来，只做这一件"],
        "week": ["固定起床时间，比固定睡觉时间更容易坚持", "减少睡前 1 小时的屏幕时间", "找一个人说说最近的状态"],
        "professional": ["如果两周后仍无改善，可以考虑一次心理咨询"],
        "tone": "watch",
    },
    "moderate": {
        "label": "中度",
        "summary": "困扰已经比较明显，开始影响日常的工作、学习或关系。",
        "signs": ["情绪波动频繁，恢复得比平时慢", "对原本感兴趣的事提不起劲", "睡眠或食欲出现明显变化", "容易疲惫，效率下降"],
        "today": ["今天先减掉一件非必要的事，允许自己少做一点", "把感受写下来，不用组织语言，写满一页就停"],
        "week": ["建立固定的作息与用餐时间，先稳住身体节律", "和信任的人明确说出「我最近不太好」", "记录情绪波动的时间点，观察触发因素"],
        "professional": ["建议预约一次专业心理咨询，做结构化评估", "若持续超过一个月，不建议继续自行调节"],
        "tone": "watch",
    },
    "severe": {
        "label": "偏重",
        "summary": "得分位于最高区间，提示困扰程度较重，建议尽快获得专业支持。",
        "signs": ["大部分时间被情绪占据，难以自行缓解", "日常功能明显受损（工作、学习、社交）", "睡眠严重紊乱，或持续躯体不适"],
        "today": ["今天不必独自硬扛，联系一个可信任的人陪着你", "把「需要帮忙」这件事具体说出来，比如陪你去挂号"],
        "week": ["尽快到精神卫生中心或医院心理科做一次面诊", "把近两周的睡眠、情绪、用药情况记录下来带过去"],
        "professional": ["建议尽快线下就诊，量表不能替代诊断", "若出现自伤念头，请立即联系当地心理援助热线或急诊"],
        "tone": "prompt",
    },
}

# 其他量表使用的等级命名，映射到四档语义后复用上面的文案
LEVEL_ALIAS = {
    "high": "none",           # 高自尊 / 高情绪稳定性 = 好
    "medium_high": "mild",
    "medium": "mild",
    "medium_low": "moderate",
    "low": "severe",
    "good": "none",           # 睡眠质量好
    "fair": "mild",
    "poor": "moderate",
    "bad": "severe",
}

# 量表特异性建议（叠加在通用建议之上，不影响等级判定）
TEST_ADVICE: Dict[str, Dict[str, List[str]]] = {
    "SAS20": {
        "today": ["焦虑上头时先做一次腹式呼吸，把注意力放回身体"],
        "week": ["减少咖啡因摄入，尤其是下午之后", "把担心的事写下来，区分「能做的」和「做不了的」"],
    },
    "SDS20": {
        "today": ["哪怕只出门走 10 分钟，也比一直躺着好"],
        "week": ["保持最低限度的社交接触，哪怕只是和人打个招呼", "避免用酒精帮助入睡"],
    },
    "STRESS20": {
        "today": ["列出压力源，圈出本周能改变的那一个"],
        "week": ["练习一次明确的拒绝，从最小的事开始", "给自己排一段「什么都不做」的时间"],
    },
    "SES10": {
        "week": ["每天记下三件做成的小事，不用宏大", "把「我不行」换成「我还没学会」"],
    },
    "LSAS20": {
        "week": ["从低压力场景开始练习社交，逐步增加难度", "事前准备一两句开场话，降低临场负担"],
    },
    "ES15": {
        "week": ["规律运动对情绪稳定性的提升通常比想象中明显", "记录情绪波动，找出高发时段"],
    },
    "MBI15": {
        "week": ["明确划定下班后的边界，工作消息不随时响应", "找回一件与工作无关、纯粹为自己做的事"],
    },
    "PSQI19": {
        "week": ["固定起床时间，周末也不超过 1 小时偏差", "床只用来睡觉，不在床上刷手机"],
    },
    "BIG5_20": {
        "week": ["了解特质是为了扬长，不是给自己贴标签", "针对得分偏低的维度设一个具体的小目标"],
    },
}

DIMENSION_BANDS = [
    (80, "偏高", "该维度得分接近上限，是需要优先关注的部分。"),
    (60, "偏高", "该维度明显高于平均，建议重点关注。"),
    (40, "中等", "该维度处于中间水平，尚在可调节范围。"),
    (0, "偏低", "该维度得分较低，暂时不是主要压力来源。"),
]


class InterpretationService:
    """把分数翻译成解读。纯函数式，不依赖数据库，便于单元测试。"""

    VERSION = "interp-v1"

    @staticmethod
    def _level_code(result_data: Dict[str, Any]) -> str:
        return (result_data.get("result_level") or "").strip()

    @staticmethod
    def _level_copy(code: str) -> Dict[str, Any]:
        if code in LEVEL_COPY:
            return LEVEL_COPY[code]
        alias = LEVEL_ALIAS.get(code)
        if alias and alias in LEVEL_COPY:
            return dict(LEVEL_COPY[alias])
        return {
            "label": "已解读",
            "summary": "该量表的等级说明尚未配置文案，可参考下方建议。",
            "signs": [],
            "today": [],
            "week": [],
            "professional": [],
            "tone": "routine",
        }

    @staticmethod
    def _parse_levels(result_rules: Optional[Dict]) -> List[Dict[str, Any]]:
        """把 result_rules.levels 解析为统一的列表。

        兼容三种历史写法：dict（SAS/SDS 等）、list（扩展量表）、缺省。
        """
        if not result_rules:
            return []
        levels = result_rules.get("levels") if isinstance(result_rules, dict) else None

        out: List[Dict[str, Any]] = []
        if isinstance(levels, dict):
            for code, cfg in levels.items():
                cfg = cfg or {}
                out.append(
                    {
                        "code": code,
                        "label": cfg.get("title") or cfg.get("label") or code,
                        "desc": cfg.get("desc") or cfg.get("description") or "",
                        "min": cfg.get("min", cfg.get("min_score")),
                        "max": cfg.get("max", cfg.get("max_score")),
                    }
                )
        elif isinstance(levels, list):
            for cfg in levels:
                if not isinstance(cfg, dict):
                    continue
                out.append(
                    {
                        "code": cfg.get("code") or cfg.get("level") or "",
                        "label": cfg.get("title") or cfg.get("label") or "",
                        "desc": cfg.get("desc") or cfg.get("description") or "",
                        "min": cfg.get("min", cfg.get("min_score")),
                        "max": cfg.get("max", cfg.get("max_score")),
                    }
                )

        out.sort(key=lambda x: (x["min"] if isinstance(x["min"], (int, float)) else 0))
        return out

    @classmethod
    def build(
        cls,
        test,
        result_data: Dict[str, Any],
        answers: Optional[Dict[Any, Any]] = None,
    ) -> Dict[str, Any]:
        code = cls._level_code(result_data)
        copy = cls._level_copy(code)
        total = result_data.get("total_score")
        rules = getattr(test, "result_rules", None)
        levels = cls._parse_levels(rules)

        # ---- 等级区间与命中情况 ----
        matched = next((lv for lv in levels if lv["code"] == code), None)
        range_info = None
        position = ""
        if matched and matched.get("min") is not None and matched.get("max") is not None:
            range_info = {"min": matched["min"], "max": matched["max"]}
            if isinstance(total, (int, float)):
                span = matched["max"] - matched["min"]
                ratio = 0 if span <= 0 else (total - matched["min"]) / span
                if ratio < 0.34:
                    position = "处于该区间下部"
                elif ratio < 0.67:
                    position = "处于该区间中部"
                else:
                    position = "处于该区间上部，接近下一档"

        thresholds = [
            {
                "code": lv["code"],
                "label": lv["label"],
                "min": lv["min"],
                "max": lv["max"],
                "matched": lv["code"] == code,
            }
            for lv in levels
        ]

        # ---- 维度解读 ----
        dimensions = []
        for dim in result_data.get("dimension_scores") or []:
            score = dim.get("score") or 0
            max_score = dim.get("max_score") or 0
            percent = round(score / max_score * 100) if max_score else None
            band, note = "未标注", "该维度未配置满分，仅展示原始分。"
            if percent is not None:
                for edge, name, text in DIMENSION_BANDS:
                    if percent >= edge:
                        band, note = name, text
                        break
            dimensions.append(
                {
                    "name": dim.get("dimension") or "未命名维度",
                    "score": score,
                    "max_score": max_score,
                    "percent": percent,
                    "band": band,
                    "note": note,
                }
            )

        # ---- 建议（通用 + 量表特异） ----
        extra = TEST_ADVICE.get(getattr(test, "test_code", "") or "", {})
        advice = {
            "today": list(dict.fromkeys(copy["today"] + extra.get("today", []))),
            "week": list(dict.fromkeys(copy["week"] + extra.get("week", []))),
            "professional": list(dict.fromkeys(copy["professional"])),
        }

        # ---- 风险提示 ----
        tone = copy["tone"]
        signal = {
            "prompt": {
                "level": "prompt",
                "title": "建议尽快获得专业支持",
                "text": "量表结果不能替代诊断。请尽快到精神卫生中心或医院心理科面诊；若出现自伤念头，请立即联系心理援助热线或急诊。",
            },
            "watch": {
                "level": "watch",
                "title": "值得持续关注",
                "text": "接下来两周留意睡眠、食欲与情绪变化。若持续加重或影响日常，建议预约专业咨询。",
            },
            "routine": {
                "level": "routine",
                "title": "保持即可",
                "text": "目前不需要额外干预，维持现有节律，定期复测观察变化。",
            },
        }[tone]

        # ---- 计分依据（用于解释的可追溯性） ----
        scoring_rules = getattr(test, "scoring_rules", None) or {}
        reverse_questions = scoring_rules.get("reverse_questions") or []
        answered = len(answers or {})
        notes = []
        if reverse_questions:
            notes.append(f"本量表含 {len(reverse_questions)} 道反向题，已按「满分+1−原始分」折算后再计入总分。")
        if range_info:
            notes.append(
                f"等级判定依据 result_rules.levels：{copy['label']}档为 {range_info['min']}–{range_info['max']} 分，本次得分 {total}。"
            )
        if getattr(test, "total_questions", None) and answered and answered < test.total_questions:
            notes.append(f"本次作答 {answered}/{test.total_questions} 题，未作答题目按最低分计入，结果可能偏低。")

        return {
            "version": cls.VERSION,
            "level": {
                "code": code,
                # 展示名优先用量表自己配置的等级名（如「轻度焦虑」），
                # 没有配置时才退回通用语义标签
                "label": (matched or {}).get("label") or copy["label"],
                "range": range_info,
                "position": position,
                "summary": (matched or {}).get("desc") or copy["summary"],
                "signs": copy["signs"],
            },
            "dimensions": dimensions,
            "advice": advice,
            "signal": signal,
            "disclaimer": "量表结果仅用于自我了解与状态观察，不构成医学诊断，也不能替代面诊。",
            "trace": {
                "thresholds": thresholds,
                "score_basis": {
                    "total_score": total,
                    "answered": answered,
                    "total_questions": getattr(test, "total_questions", None),
                    "reverse_questions": reverse_questions,
                    "dimension_sum": sum(d["score"] for d in dimensions) if dimensions else None,
                },
                "notes": notes,
            },
        }
