"""
补充心理测试数据初始化脚本
新增5套测试：自尊量表(SES)、社交焦虑量表(LSAS)、情绪稳定性量表、职业倦怠量表、睡眠质量量表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models.test import PsychologicalTest, TestQuestion


def init_ses_test(db: Session):
    """初始化自尊量表(SES-10题版)"""

    test = PsychologicalTest(
        test_code="SES10",
        title="自尊量表 (SES-10)",
        description="自尊量表（Self-Esteem Scale，SES）由Rosenberg于1965年编制，用于评估个体的整体自尊水平。本版本为10题简化版，能够快速有效地评估个体的自我价值和自我接纳程度。",
        category="personality",
        intro_text="本测试共10题，每题有4个选项。请根据您的真实情况，选择最符合的选项。",
        total_questions=10,
        score_type="total",
        option_type="4选项",
        scoring_rules={
            "type": "sum",
            "reverse_questions": [2, 5, 6, 8, 9]  # 需要反向计分的题目
        },
        result_rules={
            "levels": {
                "high": {"min": 30, "max": 40, "title": "高自尊", "desc": "自我价值感强，自信且自我接纳程度高"},
                "medium": {"min": 20, "max": 29, "title": "中等自尊", "desc": "自我价值感一般，有一定自信，偶有自我怀疑"},
                "low": {"min": 10, "max": 19, "title": "低自尊", "desc": "自我价值感较低，缺乏自信，需要提升自我接纳"}
            }
        },
        sort_order=5,
        is_active=True,
        hot_value=75
    )
    db.add(test)
    db.flush()

    ses_questions = [
        (1, "我觉得自己有很多优点", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, False),
        (2, "我觉得自己一事无成", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, True),
        (3, "我能够做得和大多数人一样好", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, False),
        (4, "我对自己持有积极的态度", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, False),
        (5, "我总的来说是失败的", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, True),
        (6, "我觉得自己没有什么值得自豪的", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, True),
        (7, "我对自已感到满意", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, False),
        (8, "我希望能更多地尊重自己", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, True),
        (9, "我有时觉得自己确实无用", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, True),
        (10, "我认为自己是个有价值的人", [{"value": 1, "label": "非常不同意"}, {"value": 2, "label": "不同意"}, {"value": 3, "label": "同意"}, {"value": 4, "label": "非常同意"}], None, False),
    ]

    for num, text, opts, dim, is_rev in ses_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=5 if is_rev else None,
            sort_order=num
        )
        db.add(question)

    print(f"✓ 自尊量表(SES) 初始化完成，共 {len(ses_questions)} 题")


def init_lsas_test(db: Session):
    """初始化社交焦虑量表(LSAS-20题版)"""

    test = PsychologicalTest(
        test_code="LSAS20",
        title="社交焦虑量表 (LSAS-20)",
        description="社交焦虑量表（Liebowitz Social Anxiety Scale，LSAS）用于评估社交恐惧和社交焦虑的程度。本版本为20题简化版，涵盖恐惧和回避两个维度。",
        category="anxiety",
        intro_text="本测试共20题，每题有4个选项。请根据您最近3个月的实际感受，选择最符合的选项。",
        total_questions=20,
        score_type="total",
        option_type="4选项",
        scoring_rules={
            "type": "sum_with_dimensions",
            "dimensions": {
                "恐惧": {"questions": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]},
                "回避": {"questions": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]}
            }
        },
        result_rules={
            "levels": {
                "none": {"min": 20, "max": 30, "title": "无明显社交焦虑", "desc": "社交场合无明显焦虑，能够正常社交"},
                "mild": {"min": 31, "max": 50, "title": "轻度社交焦虑", "desc": "在某些社交场合有轻微焦虑，不影响正常社交"},
                "moderate": {"min": 51, "max": 65, "title": "中度社交焦虑", "desc": "在多数社交场合有明显焦虑，有一定回避行为"},
                "severe": {"min": 66, "max": 80, "title": "重度社交焦虑", "desc": "在社交场合有严重焦虑，强烈回避社交，建议寻求专业帮助"}
            }
        },
        sort_order=6,
        is_active=True,
        hot_value=70
    )
    db.add(test)
    db.flush()

    lsas_questions = [
        # 恐惧维度 (奇数题)
        (1, "在公共场合打电话时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (2, "在公共场合打电话时会回避", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (3, "在小组中参与讨论时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (4, "会回避在小组中参与讨论", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (5, "与陌生人会面时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (6, "会回避与陌生人会面", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (7, "在公共场合进食时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (8, "会回避在公共场合进食", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (9, "在权威人物面前说话时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (10, "会回避在权威人物面前说话", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (11, "在公共场合表演或演讲时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (12, "会回避在公共场合表演或演讲", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (13, "去聚会或社交活动时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (14, "会回避参加聚会或社交活动", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (15, "在公共场合工作时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (16, "会回避在公共场合工作", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (17, "在公共场合书写时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (18, "会回避在公共场合书写", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
        (19, "与不太熟悉的人交流时感到恐惧或焦虑", [{"value": 1, "label": "无"}, {"value": 2, "label": "轻微"}, {"value": 3, "label": "中度"}, {"value": 4, "label": "严重"}], "恐惧", False),
        (20, "会回避与不太熟悉的人交流", [{"value": 1, "label": "从不"}, {"value": 2, "label": "偶尔"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}], "回避", False),
    ]

    for num, text, opts, dim, is_rev in lsas_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=None,
            sort_order=num
        )
        db.add(question)

    print(f"✓ 社交焦虑量表(LSAS) 初始化完成，共 {len(lsas_questions)} 题")


def init_emotional_stability_test(db: Session):
    """初始化情绪稳定性量表(15题版)"""

    test = PsychologicalTest(
        test_code="ES15",
        title="情绪稳定性量表 (15题)",
        description="情绪稳定性量表用于评估个体的情绪调节能力和情绪波动程度。高情绪稳定性意味着能够有效管理情绪，不易受外界影响。",
        category="emotion",
        intro_text="本测试共15题，每题有5个选项。请根据您最近一个月的真实情况，选择最符合的选项。",
        total_questions=15,
        score_type="total",
        option_type="5选项",
        scoring_rules={
            "type": "sum",
            "reverse_questions": [1, 4, 6, 9, 11, 13, 15]  # 需要反向计分的题目
        },
        result_rules={
            "levels": {
                "high": {"min": 60, "max": 75, "title": "情绪非常稳定", "desc": "情绪调节能力强，不易受外界影响，能够保持平和心态"},
                "medium_high": {"min": 45, "max": 59, "title": "情绪较稳定", "desc": "情绪调节能力较强，偶有波动但能快速恢复"},
                "medium_low": {"min": 30, "max": 44, "title": "情绪稳定性一般", "desc": "情绪波动较明显，需要提升情绪管理能力"},
                "low": {"min": 15, "max": 29, "title": "情绪不稳定", "desc": "情绪波动大，易受外界影响，建议学习情绪调节技巧"}
            }
        },
        sort_order=7,
        is_active=True,
        hot_value=65
    )
    db.add(test)
    db.flush()

    es_questions = [
        (1, "我容易因为小事而生气", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (2, "我能够控制自己的情绪", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (3, "我在压力下能保持冷静", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (4, "我的情绪变化很快", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (5, "我能够从负面情绪中快速恢复", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (6, "我经常感到情绪低落", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (7, "我能够理性地处理问题", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (8, "我不易被他人的情绪影响", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (9, "我经常感到焦虑不安", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (10, "我能够保持平和的心态", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (11, "我容易激动或冲动", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (12, "我能够应对突发状况", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (13, "我经常情绪波动", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
        (14, "我能够积极看待问题", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, False),
        (15, "我容易被小事困扰", [{"value": 1, "label": "从不"}, {"value": 2, "label": "很少"}, {"value": 3, "label": "有时"}, {"value": 4, "label": "经常"}, {"value": 5, "label": "总是"}], None, True),
    ]

    for num, text, opts, dim, is_rev in es_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=6 if is_rev else None,
            sort_order=num
        )
        db.add(question)

    print(f"✓ 情绪稳定性量表 初始化完成，共 {len(es_questions)} 题")


def init_burnout_test(db: Session):
    """初始化职业倦怠量表(15题版)"""

    test = PsychologicalTest(
        test_code="MBI15",
        title="职业倦怠量表 (15题)",
        description="职业倦怠量表（Maslach Burnout Inventory）用于评估职业倦怠的程度，包含情绪衰竭、去人格化、个人成就感降低三个维度。",
        category="work",
        intro_text="本测试共15题，每题有7个选项。请根据您最近在工作中的真实感受，选择最符合的选项。",
        total_questions=15,
        score_type="total",
        option_type="7选项",
        scoring_rules={
            "type": "sum_with_dimensions",
            "dimensions": {
                "情绪衰竭": {"questions": [1, 2, 3, 4, 5]},
                "去人格化": {"questions": [6, 7, 8, 9, 10]},
                "个人成就感": {"questions": [11, 12, 13, 14, 15]}
            },
            "reverse_questions": [11, 12, 13, 14, 15]  # 个人成就感维度需要反向计分
        },
        result_rules={
            "levels": {
                "none": {"min": 15, "max": 35, "title": "无职业倦怠", "desc": "工作状态良好，无明显倦怠表现"},
                "mild": {"min": 36, "max": 60, "title": "轻度倦怠", "desc": "偶尔感到工作疲惫，需要适当休息和调整"},
                "moderate": {"min": 61, "max": 85, "title": "中度倦怠", "desc": "经常感到工作疲惫，对工作有疏离感，需要关注工作与生活的平衡"},
                "severe": {"min": 86, "max": 105, "title": "重度倦怠", "desc": "严重职业倦怠，情绪耗竭，建议寻求职业咨询和心理支持"}
            }
        },
        sort_order=8,
        is_active=True,
        hot_value=60
    )
    db.add(test)
    db.flush()

    mbi_questions = [
        # 情绪衰竭维度
        (1, "我感到工作耗尽了我的精力", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "情绪衰竭", False),
        (2, "我感到工作让我筋疲力尽", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "情绪衰竭", False),
        (3, "我感到一天工作结束后就累得不想做任何事", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "情绪衰竭", False),
        (4, "我能够有效应对工作中的问题", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "情绪衰竭", True),
        (5, "我感到面对工作时无力应对", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "情绪衰竭", False),
        # 去人格化维度
        (6, "我对工作对象（同事/客户）的态度冷漠", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "去人格化", False),
        (7, "我感到工作对象（同事/客户）将问题归咎于我", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "去人格化", False),
        (8, "我对工作对象（同事/客户）缺乏同情心", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "去人格化", False),
        (9, "我感到工作对象（同事/客户）让我感到烦躁", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "去人格化", False),
        (10, "我怀疑自己工作的意义", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "去人格化", False),
        # 个人成就感维度（反向题）
        (11, "我能够有效地处理工作对象（同事/客户）的问题", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "个人成就感", True),
        (12, "我感到自己通过工作积极影响了他人", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "个人成就感", True),
        (13, "我在工作中能够保持冷静", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "个人成就感", True),
        (14, "我在工作中创造了有价值的东西", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "个人成就感", True),
        (15, "我对自己的工作成果感到满意", [{"value": 1, "label": "从不"}, {"value": 2, "label": "一年几次"}, {"value": 3, "label": "一个月一次"}, {"value": 4, "label": "一个月几次"}, {"value": 5, "label": "每周一次"}, {"value": 6, "label": "每天"}, {"value": 7, "label": "每天多次"}], "个人成就感", True),
    ]

    for num, text, opts, dim, is_rev in mbi_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=8 if is_rev else None,  # 7选项反向: 1->7, 2->6, 3->5, 4->4, 5->3, 6->2, 7->1
            sort_order=num
        )
        db.add(question)

    print(f"✓ 职业倦怠量表(MBI) 初始化完成，共 {len(mbi_questions)} 题")


def init_sleep_test(db: Session):
    """初始化睡眠质量量表(PSQI-19题版)"""

    test = PsychologicalTest(
        test_code="PSQI19",
        title="匹茨堡睡眠质量指数 (PSQI-19)",
        description="匹茨堡睡眠质量指数（Pittsburgh Sleep Quality Index，PSQI）用于评估最近一个月的睡眠质量，涵盖睡眠时长、入睡时间、睡眠效率、睡眠障碍等多个维度。",
        category="health",
        intro_text="本测试共19题，请根据您最近一个月的实际睡眠情况，选择最符合的选项。",
        total_questions=19,
        score_type="total",
        option_type="多选项",
        scoring_rules={
            "type": "weighted_sum",  # 各题目权重不同
            "dimensions": {
                "主观睡眠质量": {"questions": [6]},
                "入睡时间": {"questions": [2, 5]},
                "睡眠时间": {"questions": [4]},
                "睡眠效率": {"questions": [1, 2, 3, 4]},
                "睡眠障碍": {"questions": [5, 7, 8, 9, 10, 11, 12, 13]},
                "日间功能障碍": {"questions": [14, 15, 16, 17]}
            }
        },
        result_rules={
            "levels": {
                "good": {"min": 0, "max": 5, "title": "睡眠质量很好", "desc": "睡眠质量优秀，保持良好作息"},
                "fair": {"min": 6, "max": 10, "title": "睡眠质量尚可", "desc": "睡眠质量一般，偶尔有睡眠问题"},
                "poor": {"min": 11, "max": 21, "title": "睡眠质量差", "desc": "存在明显睡眠问题，建议改善睡眠习惯或寻求专业帮助"}
            }
        },
        sort_order=9,
        is_active=True,
        hot_value=80
    )
    db.add(test)
    db.flush()

    psqi_questions = [
        (1, "通常晚上几点上床？", [{"value": 0, "label": "22:00前"}, {"value": 1, "label": "22:00-23:00"}, {"value": 2, "label": "23:00-24:00"}, {"value": 3, "label": "0:00后"}], None, False),
        (2, "从上床到睡着通常需要多少分钟？", [{"value": 0, "label": "≤15分钟"}, {"value": 1, "label": "16-30分钟"}, {"value": 2, "label": "31-60分钟"}, {"value": 3, "label": ">60分钟"}], None, False),
        (3, "通常早上几点起床？", [{"value": 0, "label": "6:00前"}, {"value": 1, "label": "6:00-7:00"}, {"value": 2, "label": "7:00-8:00"}, {"value": 3, "label": "8:00后"}], None, False),
        (4, "每晚实际睡眠时间（不含躺床时间）", [{"value": 0, "label": ">7小时"}, {"value": 1, "label": "6-7小时"}, {"value": 2, "label": "5-6小时"}, {"value": 3, "label": "<5小时"}], None, False),
        (5, "最近一个月是否因以下原因影响睡眠：无法在30分钟内入睡", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (6, "整体评价最近一个月的睡眠质量", [{"value": 0, "label": "很好"}, {"value": 1, "label": "较好"}, {"value": 2, "label": "一般"}, {"value": 3, "label": "较差"}], None, False),
        (7, "是否因以下原因影响睡眠：夜间或早晨早醒", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (8, "是否因以下原因影响睡眠：起床上厕所", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (9, "是否因以下原因影响睡眠：呼吸不畅或咳嗽", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (10, "是否因以下原因影响睡眠：感觉太冷或太热", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (11, "是否因以下原因影响睡眠：做噩梦", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (12, "是否因以下原因影响睡眠：身体疼痛不适", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (13, "其他影响睡眠的问题（如打鼾、腿抽动等）", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (14, "最近一个月是否在起床时感到疲倦", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (15, "最近一个月是否在日常活动中保持困倦状态", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (16, "最近一个月是否在活动中需要保持清醒时感到困倦", [{"value": 0, "label": "无"}, {"value": 1, "label": "<1次/周"}, {"value": 2, "label": "1-2次/周"}, {"value": 3, "label": "≥3次/周"}], None, False),
        (17, "最近一个月是否在起床后精力充沛", [{"value": 0, "label": "总是"}, {"value": 1, "label": "多数时候"}, {"value": 2, "label": "少数时候"}, {"value": 3, "label": "从不"}], None, False),
        (18, "与大多数人相比，您的睡眠质量", [{"value": 0, "label": "明显更好"}, {"value": 1, "label": "稍好一些"}, {"value": 2, "label": "差不多"}, {"value": 3, "label": "稍差一些"}], None, False),
        (19, "与大多数人相比，您的睡眠时长", [{"value": 0, "label": "明显更长"}, {"value": 1, "label": "稍长一些"}, {"value": 2, "label": "差不多"}, {"value": 3, "label": "稍短一些"}], None, False),
    ]

    for num, text, opts, dim, is_rev in psqi_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=None,
            sort_order=num
        )
        db.add(question)

    print(f"✓ 匹茨堡睡眠质量指数(PSQI) 初始化完成，共 {len(psqi_questions)} 题")


def main():
    """主函数"""
    print("=" * 50)
    print("补充心理测试数据初始化")
    print("=" * 50)

    # 创建数据库表
    print("\n正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")

    # 获取数据库会话
    db = SessionLocal()

    try:
        # 检查是否已有测试数据
        existing_tests = db.query(PsychologicalTest).count()
        print(f"\n当前数据库中有 {existing_tests} 套测试")

        print("\n开始初始化补充测试数据...\n")

        # 初始化各套测试
        init_ses_test(db)
        init_lsas_test(db)
        init_emotional_stability_test(db)
        init_burnout_test(db)
        init_sleep_test(db)

        # 提交事务
        db.commit()

        print("\n" + "=" * 50)
        print("✓ 补充测试数据初始化完成！")
        print("=" * 50)

        # 显示统计信息
        test_count = db.query(PsychologicalTest).count()
        question_count = db.query(TestQuestion).count()
        print(f"\n统计信息：")
        print(f"  - 总测试套数: {test_count}")
        print(f"  - 总题目数: {question_count}")
        print(f"  - 新增测试套数: 5")
        print(f"  - 新增题目数: 79")

    except Exception as e:
        db.rollback()
        print(f"\n✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
