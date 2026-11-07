"""
心理测试数据初始化脚本
包含4套测试：焦虑自评量表(SAS)、抑郁自评量表(SDS)、大五人格量表、工作生活压力量表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models.test import PsychologicalTest, TestQuestion
from app.models.user import User


def init_sas_test(db: Session):
    """初始化焦虑自评量表(SAS-20题版)"""

    # 创建测试记录
    test = PsychologicalTest(
        test_code="SAS20",
        title="焦虑自评量表 (SAS-20)",
        description="焦虑自评量表（Self-Rating Anxiety Scale，SAS）是由Zung于1971年编制的，用于评估焦虑程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的焦虑水平。",
        category="anxiety",
        intro_text="本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。",
        total_questions=20,
        score_type="total",
        option_type="4选项",
        scoring_rules={
            "type": "sum_with_dimensions",
            "dimensions": {
                "躯体性焦虑": {"questions": [2, 4, 6, 8, 9, 10, 12, 14]},
                "精神性焦虑": {"questions": [1, 3, 5, 7, 11, 13, 15, 16, 17, 18, 19, 20]}
            },
            "reverse_questions": [5, 9, 13, 17, 19]  # 需要反向计分的题目
        },
        result_rules={
            "levels": {
                "none": {"min": 20, "max": 30, "title": "无焦虑", "desc": "情绪状态良好，无明显焦虑表现"},
                "mild": {"min": 31, "max": 45, "title": "轻度焦虑", "desc": "偶尔出现焦虑表现，不影响日常工作与生活"},
                "moderate": {"min": 46, "max": 60, "title": "中度焦虑", "desc": "频繁出现焦虑表现，对日常工作与生活有一定影响"},
                "severe": {"min": 61, "max": 80, "title": "重度焦虑", "desc": "持续出现严重焦虑表现，严重影响日常工作与生活，建议寻求专业心理咨询"}
            }
        },
        sort_order=1,
        is_active=True,
        hot_value=100
    )
    db.add(test)
    db.flush()

    # 创建题目
    sas_questions = [
        (1, "我感到比往常更加神经过敏和焦虑", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (2, "我无缘无故感到担心", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (3, "我容易心烦意乱或感到恐慌", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (4, "我感到身体疲乏无力", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (5, "我感到平静，能安静坐着", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", True),
        (6, "我感到心跳加快或呼吸不畅", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (7, "我感到头痛或胃痛", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (8, "我感到手脚麻木或刺痛", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (9, "我感到平静和放松", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", True),
        (10, "我感到尿频或排便频繁", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (11, "我感到害怕，好像有什么可怕的事情发生", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (12, "我感到手脚发抖或颤抖", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (13, "我感到自信和愉快", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", True),
        (14, "我感到容易入睡和睡眠安稳", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体性焦虑", False),
        (15, "我感到做噩梦或惊醒", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (16, "我感到面部潮红或发热", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (17, "我感到高兴和愉快", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", True),
        (18, "我感到口干舌燥", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
        (19, "我感到事情都在我的掌控之中", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", True),
        (20, "我感到难以集中注意力", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "精神性焦虑", False),
    ]

    for num, text, opts, dim, is_rev in sas_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=5 if is_rev else None,  # 反向计分: 1->4, 2->3, 3->2, 4->1
            sort_order=num
        )
        db.add(question)

    print(f"✓ 焦虑自评量表(SAS) 初始化完成，共 {len(sas_questions)} 题")


def init_sds_test(db: Session):
    """初始化抑郁自评量表(SDS-20题版)"""

    test = PsychologicalTest(
        test_code="SDS20",
        title="抑郁自评量表 (SDS-20)",
        description="抑郁自评量表（Self-Rating Depression Scale，SDS）是由Zung于1965年编制的，用于评估抑郁程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的抑郁水平。",
        category="depression",
        intro_text="本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。",
        total_questions=20,
        score_type="total",
        option_type="4选项",
        scoring_rules={
            "type": "sum_with_dimensions",
            "dimensions": {
                "情绪低落": {"questions": [1, 3, 5, 7, 9, 15, 17, 19]},
                "兴趣减退": {"questions": [2, 4, 6, 11, 14]},
                "躯体症状": {"questions": [8, 10, 12, 13, 16, 18, 20]}
            },
            "reverse_questions": [2, 5, 6, 11, 12, 14, 16, 17, 18, 20]  # 需要反向计分的题目
        },
        result_rules={
            "levels": {
                "none": {"min": 20, "max": 30, "title": "无抑郁", "desc": "情绪状态良好，无明显抑郁表现"},
                "mild": {"min": 31, "max": 45, "title": "轻度抑郁", "desc": "偶尔出现抑郁表现，可通过自我调节缓解"},
                "moderate": {"min": 46, "max": 60, "title": "中度抑郁", "desc": "频繁出现抑郁表现，自我调节效果有限，建议寻求心理疏导"},
                "severe": {"min": 61, "max": 80, "title": "重度抑郁", "desc": "持续出现严重抑郁表现，影响正常生活，需及时寻求专业心理咨询与治疗"}
            }
        },
        sort_order=2,
        is_active=True,
        hot_value=95
    )
    db.add(test)
    db.flush()

    sds_questions = [
        (1, "我感到情绪沮丧，郁闷", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (2, "我感到早晨心情最好", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "兴趣减退", True),
        (3, "我要哭或想哭", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (4, "我夜间睡眠不好", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "兴趣减退", False),
        (5, "我吃饭像平时一样多", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", True),
        (6, "我的性功能正常", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "兴趣减退", True),
        (7, "我感到体重减轻", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (8, "我为便秘烦恼", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", False),
        (9, "我的心跳比平时快", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (10, "我无故感到疲劳", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", False),
        (11, "我的头脑像往常一样清楚", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "兴趣减退", True),
        (12, "我做事情像平时一样不感到困难", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", True),
        (13, "我坐卧不安，难以保持平静", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", False),
        (14, "我对未来感到有希望", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "兴趣减退", True),
        (15, "我比平时更容易激怒", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (16, "我觉得决定什么事很容易", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", True),
        (17, "我感到自己是有用的和不可缺少的人", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", True),
        (18, "我的生活很有意义", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", True),
        (19, "我感到若是我死了别人会过得更好", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "情绪低落", False),
        (20, "我依旧喜爱平时喜爱的事物", [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}], "躯体症状", True),
    ]

    for num, text, opts, dim, is_rev in sds_questions:
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

    print(f"✓ 抑郁自评量表(SDS) 初始化完成，共 {len(sds_questions)} 题")


def init_big5_test(db: Session):
    """初始化大五人格简版量表(20题版)"""

    test = PsychologicalTest(
        test_code="BIG5_20",
        title="大五人格简版量表 (20题)",
        description="大五人格量表（Big Five Inventory）是国际公认的人格测评工具，从开放性、责任心、外倾性、宜人性、神经质五个维度全面评估人格特质。本版本为20题简版，快速准确地了解您的人格特征。",
        category="personality",
        intro_text="本测试共20题，每题有5个选项。请根据您的真实情况，选择最符合的选项。",
        total_questions=20,
        score_type="dimension",
        option_type="5选项",
        scoring_rules={
            "type": "dimension_sum",
            "dimensions": {
                "开放性(O)": {"questions": {1: False, 6: False, 11: False, 16: True}},
                "责任心(C)": {"questions": {2: False, 7: False, 12: False, 17: True}},
                "外倾性(E)": {"questions": {3: False, 8: False, 13: False, 18: True}},
                "宜人性(A)": {"questions": {4: False, 9: False, 14: False, 19: True}},
                "神经质(N)": {"questions": {5: False, 10: False, 15: False, 20: True}}
            }
        },
        result_rules={
            "levels": {
                "low": {"min": 4, "max": 8, "desc": "该维度人格特质极不明显"},
                "medium": {"min": 9, "max": 16, "desc": "该维度人格特质中等，表现均衡"},
                "high": {"min": 17, "max": 20, "desc": "该维度人格特质非常明显"}
            }
        },
        sort_order=3,
        is_active=True,
        hot_value=80
    )
    db.add(test)
    db.flush()

    big5_questions = [
        # 开放性 (O)
        (1, "我喜欢尝试新的食物和旅行", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "开放性", False),
        # 责任心 (C)
        (2, "我做事总是有条不紊", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "责任心", False),
        # 外倾性 (E)
        (3, "我善于与人交谈", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "外倾性", False),
        # 宜人性 (A)
        (4, "我倾向于信任他人", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "宜人性", False),
        # 神经质 (N)
        (5, "我容易紧张和焦虑", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "神经质", False),
        # 开放性 (O)
        (6, "我对抽象概念感兴趣", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "开放性", False),
        # 责任心 (C)
        (7, "我做事总是尽心尽力", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "责任心", False),
        # 外倾性 (E)
        (8, "我能在社交场合中活跃气氛", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "外倾性", False),
        # 宜人性 (A)
        (9, "我乐于帮助他人", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "宜人性", False),
        # 神经质 (N)
        (10, "我情绪波动较大", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "神经质", False),
        # 开放性 (O)
        (11, "我喜欢思考复杂的理论问题", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "开放性", False),
        # 责任心 (C)
        (12, "我做事总是会提前计划", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "责任心", False),
        # 外倾性 (E)
        (13, "我喜欢与人打交道", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "外倾性", False),
        # 宜人性 (A)
        (14, "我容易体谅他人的感受", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "宜人性", False),
        # 神经质 (N)
        (15, "我容易感到沮丧", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "神经质", False),
        # 开放性 (O) - 反向题
        (16, "我更喜欢熟悉的事物而非新事物", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "开放性", True),
        # 责任心 (C) - 反向题
        (17, "我做事比较随意，不太注重细节", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "责任心", True),
        # 外倾性 (E) - 反向题
        (18, "我更喜欢独处而非社交", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "外倾性", True),
        # 宜人性 (A) - 反向题
        (19, "我倾向于怀疑他人的动机", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "宜人性", True),
        # 神经质 (N) - 反向题
        (20, "我的情绪非常稳定", [{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}], "神经质", True),
    ]

    for num, text, opts, dim, is_rev in big5_questions:
        question = TestQuestion(
            test_id=test.id,
            question_number=num,
            question_text=text,
            options=opts,
            dimension=dim,
            is_reverse=is_rev,
            reverse_value=6 if is_rev else None,  # 5选项反向: 1->5, 2->4, 3->3, 4->2, 5->1
            sort_order=num
        )
        db.add(question)

    print(f"✓ 大五人格量表 初始化完成，共 {len(big5_questions)} 题")


def init_stress_test(db: Session):
    """初始化工作生活压力量表(20题版)"""

    test = PsychologicalTest(
        test_code="STRESS20",
        title="工作生活压力量表 (20题)",
        description="工作生活压力量表用于全面评估个体在工作/学习、生活、人际关系三大维度的压力状况，帮助识别压力来源并采取有效的应对措施。",
        category="stress",
        intro_text="本测试共20题，每题有4个选项。请根据您最近一个月的实际感受，选择最符合的选项。",
        total_questions=20,
        score_type="total",
        option_type="4选项",
        scoring_rules={
            "type": "sum_with_dimensions",
            "dimensions": {
                "工作/学习压力": {"questions": [1, 4, 7, 10, 13, 16, 19]},
                "生活压力": {"questions": [2, 5, 8, 11, 14, 17]},
                "人际关系压力": {"questions": [3, 6, 9, 12, 15, 18, 20]}
            },
            "reverse_questions": []  # 无反向题
        },
        result_rules={
            "levels": {
                "none": {"min": 20, "max": 30, "title": "无压力", "desc": "整体状态轻松，各方面无明显压力，身心状态良好"},
                "mild": {"min": 31, "max": 45, "title": "轻微压力", "desc": "偶尔出现压力表现，可通过自我调节（如运动、休息）快速缓解"},
                "moderate": {"min": 46, "max": 60, "title": "中度压力", "desc": "频繁感受到压力，对日常工作/生活有一定影响，需通过合理的方式疏导压力"},
                "severe": {"min": 61, "max": 80, "title": "重度压力", "desc": "长期处于高压状态，身心俱疲，严重影响工作/生活与人际关系，建议寻求心理疏导与压力调节指导"}
            }
        },
        sort_order=4,
        is_active=True,
        hot_value=85
    )
    db.add(test)
    db.flush()

    stress_questions = [
        # 工作/学习压力
        (1, "工作任务/学习负担过重", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (2, "经济状况紧张", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (3, "与家人关系紧张", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (4, "工作/学习时间过长", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (5, "家务负担过重", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (6, "与同事/同学关系紧张", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (7, "对工作/学习表现感到焦虑", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (8, "照顾家庭责任过重", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (9, "社交压力较大", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (10, "面临职业/学业发展压力", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (11, "居住环境不佳", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (12, "与伴侣/配偶关系紧张", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (13, "工作/学习目标不明确", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (14, "缺乏个人时间", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (15, "感到孤独或被排斥", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (16, "担心工作/学习稳定性", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 生活压力
        (17, "家庭期望过高", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "生活压力", False),
        # 人际关系压力
        (18, "人际冲突处理困难", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
        # 工作/学习压力
        (19, "工作/学习与生活平衡困难", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "工作/学习压力", False),
        # 人际关系压力
        (20, "缺乏社会支持系统", [{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}], "人际关系压力", False),
    ]

    for num, text, opts, dim, is_rev in stress_questions:
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

    print(f"✓ 工作生活压力量表 初始化完成，共 {len(stress_questions)} 题")


def main():
    """主函数"""
    print("=" * 50)
    print("心理测试数据初始化")
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
        if existing_tests > 0:
            print(f"\n数据库中已存在 {existing_tests} 套测试，是否清空并重新初始化？(y/n): ", end="")
            choice = input().lower()
            if choice == 'y':
                db.query(TestQuestion).delete()
                db.query(PsychologicalTest).delete()
                db.commit()
                print("✓ 已清空现有测试数据")
            else:
                print("取消初始化")
                return

        print("\n开始初始化测试数据...\n")

        # 初始化各套测试
        init_sas_test(db)
        init_sds_test(db)
        init_big5_test(db)
        init_stress_test(db)

        # 提交事务
        db.commit()

        print("\n" + "=" * 50)
        print("✓ 所有测试数据初始化完成！")
        print("=" * 50)

        # 显示统计信息
        test_count = db.query(PsychologicalTest).count()
        question_count = db.query(TestQuestion).count()
        print(f"\n统计信息：")
        print(f"  - 测试套数: {test_count}")
        print(f"  - 题目总数: {question_count}")

    except Exception as e:
        db.rollback()
        print(f"\n✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
