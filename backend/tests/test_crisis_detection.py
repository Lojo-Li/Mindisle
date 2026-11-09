"""
风险判定规则测试

运行：
    cd backend
    pytest tests/test_crisis_detection.py -v

这些用例对应验收清单里"危险信号安全分流"一节，
核心是两件事：该报的必须报，不该报的不能乱报。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app.services.crisis_service import detect_risk, detect_crisis, LEVEL_ACTIONS


@pytest.mark.parametrize("text,expected", [
    # ── L3 必须命中 ──
    ("我想自杀", 3),
    ("我不想活了", 3),
    ("我实在活不下去了", 3),
    ("我绝望到不想活了", 3),
    ("我不开心，不想活了", 3),
    ("我已经准备好了药，想结束生命", 3),
    # ── L2 必须命中 ──
    ("我想死", 2),
    ("我最近很绝望，感觉撑不住了", 2),
    ("每天都在自残", 2),
    # ── L1 必须命中 ──
    ("我对未来没有希望", 1),
    ("我觉得活着没有意义", 1),
    # ── 不该误报 ──
    ("我没有想自杀，只是随便问问", 0),
    ("我从来没想过自残", 0),
    ("我快笑死了", 0),
    ("你找死啊", 0),
    ("今天天气不错", 0),
    ("", 0),
    ("我没有不想活", 0),
    ("我不是没有希望，只是有点累", 0),
])
def test_detect_level(text, expected):
    assert detect_risk(text).level == expected


def test_keywords_are_reported():
    """命中的关键词要能回传，否则后台工单看不懂为什么被判风险"""
    verdict = detect_risk("我最近很绝望，感觉撑不住了")
    assert verdict.level == 2
    assert "绝望" in verdict.keywords


def test_actions_match_level():
    """分级动作矩阵不能错位，否则前端不知道该弹横幅还是弹层"""
    assert detect_risk("今天天气不错").actions == []
    assert "gentle_hint" in detect_risk("我对未来没有希望").actions
    assert "banner" in detect_risk("我想死").actions
    assert "blocking_dialog" in detect_risk("我想自杀").actions


def test_hotlines_only_for_high_level():
    """L1 不该弹热线，只在 L2 以上提供"""
    assert detect_risk("我对未来没有希望").hotlines == []
    assert len(detect_risk("我想死").hotlines) > 0


def test_backward_compatible_api():
    """旧调用方仍能用 detect_crisis 拿到 (level, keywords)"""
    level, keywords = detect_crisis("我想自杀")
    assert level == 3
    assert "自杀" in keywords
