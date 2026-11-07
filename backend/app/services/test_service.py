"""
心理测试服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_, text
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os

from app.models.test import PsychologicalTest, TestQuestion, TestResult, TestProgress
from app.models.user import User
from app.schemas.test import (
    TestListQuery, SaveProgressRequest, SubmitTestRequest,
    QuestionSchema, TestDetailSchema, TestResultSchema,
    DimensionScoreSchema, TestHistoryItemSchema, TrendDataPointSchema
)
from app.services.ai_service import AIService


class TestService:
    """心理测试服务"""

    @staticmethod
    def get_test_list(db: Session, query: TestListQuery, current_user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取测试列表（包含统计数据）"""
        # 构建查询
        q = db.query(PsychologicalTest).filter(PsychologicalTest.is_active == True)

        # 关键词搜索
        if query.keyword:
            q = q.filter(
                or_(
                    PsychologicalTest.title.contains(query.keyword),
                    PsychologicalTest.description.contains(query.keyword)
                )
            )

        # 分类筛选
        if query.category:
            q = q.filter(PsychologicalTest.category == query.category)

        # 总数
        total = q.count()

        # 分页
        offset = (query.page - 1) * query.page_size
        items = q.offset(offset).limit(query.page_size).all()

        # 为每个测试添加统计数据
        items_with_stats = []
        for item in items:
            # 统计参与人数（排除已删除的记录）
            participant_count = db.query(TestResult).filter(
                and_(
                    TestResult.test_id == item.id,
                    TestResult.is_deleted == False
                )
            ).count()

            # 计算平均完成时长（分钟）
            # 使用原生SQL表达式
            try:
                result = db.execute(
                    text("""
                        SELECT AVG(TIMESTAMPDIFF(SECOND, created_at, completed_at)) / 60
                        FROM test_results
                        WHERE test_id = :test_id
                          AND is_deleted = 0
                          AND completed_at IS NOT NULL
                    """),
                    {"test_id": item.id}
                ).scalar()
                avg_duration_minutes = int(result) if result else int(item.total_questions * 0.5)
            except Exception:
                # 如果计算失败，使用默认值
                avg_duration_minutes = int(item.total_questions * 0.5)

            # 添加统计信息到测试对象
            item_dict = {
                "id": item.id,
                "test_code": item.test_code,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "intro_text": item.intro_text,
                "total_questions": item.total_questions,
                "option_type": item.option_type,
                "hot_value": item.hot_value,
                # 统计数据
                "participant_count": participant_count,
                "avg_duration": avg_duration_minutes
            }
            items_with_stats.append(item_dict)

        return {
            "total": total,
            "items": items_with_stats,
            "page": query.page,
            "page_size": query.page_size
        }

    @staticmethod
    def get_test_detail(db: Session, test_id: int) -> Optional[PsychologicalTest]:
        """获取测试详情"""
        return db.query(PsychologicalTest).filter(
            PsychologicalTest.id == test_id,
            PsychologicalTest.is_active == True
        ).first()

    @staticmethod
    def start_test(db: Session, test_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """开始测试 - 获取测试题目"""
        test = db.query(PsychologicalTest).filter(
            PsychologicalTest.id == test_id,
            PsychologicalTest.is_active == True
        ).first()

        if not test:
            return None

        # 获取题目
        questions = db.query(TestQuestion).filter(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.question_number).all()

        # 转换为 Schema
        question_schemas = [
            QuestionSchema(
                id=q.id,
                question_number=q.question_number,
                question_text=q.question_text,
                options=q.options,
                dimension=q.dimension,
                is_reverse=q.is_reverse
            )
            for q in questions
        ]

        return {
            "test_id": test.id,
            "test_code": test.test_code,
            "title": test.title,
            "intro_text": test.intro_text,
            "option_type": test.option_type,
            "questions": question_schemas
        }

    @staticmethod
    def save_progress(db: Session, user_id: int, test_id: int, request: SaveProgressRequest) -> bool:
        """保存答题进度"""
        # 查找是否已有进度记录
        progress = db.query(TestProgress).filter(
            and_(
                TestProgress.user_id == user_id,
                TestProgress.test_id == test_id
            )
        ).first()

        if progress:
            # 更新现有进度
            progress.answers = request.answers
            progress.current_question = max(request.answers.keys()) if request.answers else 1
        else:
            # 创建新进度记录
            progress = TestProgress(
                user_id=user_id,
                test_id=test_id,
                answers=request.answers,
                current_question=max(request.answers.keys()) if request.answers else 1
            )
            db.add(progress)

        db.commit()
        return True

    @staticmethod
    def _reverse_score(value: int, max_value: int) -> int:
        """反向计分"""
        return max_value - value + 1

    @staticmethod
    def _calculate_sas_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算焦虑自评量表(SAS)分数"""
        # 躯体性焦虑: 第2,4,6,8,9,10,12,14题
        physical_questions = [2, 4, 6, 8, 9, 10, 12, 14]
        # 精神性焦虑: 第1,3,5,7,11,13,15,16,17,18,19,20题
        mental_questions = [1, 3, 5, 7, 11, 13, 15, 16, 17, 18, 19, 20]

        physical_score = sum(answers.get(q, 1) for q in physical_questions)
        mental_score = sum(answers.get(q, 1) for q in mental_questions)
        total_score = physical_score + mental_score

        # 结果等级判定
        if total_score <= 30:
            level = "none"
            title = "无焦虑"
            description = "情绪状态良好，无明显焦虑表现"
        elif total_score <= 45:
            level = "mild"
            title = "轻度焦虑"
            description = "偶尔出现焦虑表现，不影响日常工作与生活"
        elif total_score <= 60:
            level = "moderate"
            title = "中度焦虑"
            description = "频繁出现焦虑表现，对日常工作与生活有一定影响"
        else:
            level = "severe"
            title = "重度焦虑"
            description = "持续出现严重焦虑表现，严重影响日常工作与生活，建议寻求专业心理咨询"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "躯体性焦虑", "score": physical_score, "max_score": 32, "level": level},
                {"dimension": "精神性焦虑", "score": mental_score, "max_score": 48, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_sds_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算抑郁自评量表(SDS)分数"""
        # 情绪低落: 第1,3,5,7,9,15,17,19题
        emotional_questions = [1, 3, 5, 7, 9, 15, 17, 19]
        # 兴趣减退: 第2,4,6,11,14题
        interest_questions = [2, 4, 6, 11, 14]
        # 躯体症状: 第8,10,12,13,16,18,20题
        physical_questions = [8, 10, 12, 13, 16, 18, 20]

        emotional_score = sum(answers.get(q, 1) for q in emotional_questions)
        interest_score = sum(answers.get(q, 1) for q in interest_questions)
        physical_score = sum(answers.get(q, 1) for q in physical_questions)
        total_score = emotional_score + interest_score + physical_score

        # 结果等级判定
        if total_score <= 30:
            level = "none"
            title = "无抑郁"
            description = "情绪状态良好，无明显抑郁表现"
        elif total_score <= 45:
            level = "mild"
            title = "轻度抑郁"
            description = "偶尔出现抑郁表现，可通过自我调节缓解"
        elif total_score <= 60:
            level = "moderate"
            title = "中度抑郁"
            description = "频繁出现抑郁表现，自我调节效果有限，建议寻求心理疏导"
        else:
            level = "severe"
            title = "重度抑郁"
            description = "持续出现严重抑郁表现，影响正常生活，需及时寻求专业心理咨询与治疗"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "情绪低落", "score": emotional_score, "max_score": 32, "level": level},
                {"dimension": "兴趣减退", "score": interest_score, "max_score": 20, "level": level},
                {"dimension": "躯体症状", "score": physical_score, "max_score": 28, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_big5_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算大五人格量表分数"""
        # 开放性(O): 第1,6,11,16题
        openness_questions = {1: False, 6: False, 11: False, 16: True}  # 16为反向题
        # 责任心(C): 第2,7,12,17题
        conscientiousness_questions = {2: False, 7: False, 12: False, 17: True}  # 17为反向题
        # 外倾性(E): 第3,8,13,18题
        extraversion_questions = {3: False, 8: False, 13: False, 18: True}  # 18为反向题
        # 宜人性(A): 第4,9,14,19题
        agreeableness_questions = {4: False, 9: False, 14: False, 19: True}  # 19为反向题
        # 神经质(N): 第5,10,15,20题
        neuroticism_questions = {5: False, 10: False, 15: False, 20: True}  # 20为反向题

        def calc_dimension(questions_dict):
            score = 0
            for q, is_reverse in questions_dict.items():
                value = answers.get(q, 3)
                if is_reverse:
                    score += TestService._reverse_score(value, 5)
                else:
                    score += value
            return score

        openness_score = calc_dimension(openness_questions)
        conscientiousness_score = calc_dimension(conscientiousness_questions)
        extraversion_score = calc_dimension(extraversion_questions)
        agreeableness_score = calc_dimension(agreeableness_questions)
        neuroticism_score = calc_dimension(neuroticism_questions)

        # 维度等级判定
        def get_level(score):
            if score <= 8:
                return "low", "极不明显"
            elif score <= 16:
                return "medium", "中等"
            else:
                return "high", "非常明显"

        def get_dimension_desc(dimension, score, level, level_text):
            desc_map = {
                "开放性": {"low": "对新事物持保守态度，偏好熟悉环境", "medium": "对新事物保持适度开放", "high": "对新事物充满好奇，乐于探索"},
                "责任心": {"low": "较为随性，不喜欢过多计划", "medium": "有一定计划性，能够完成任务", "high": "极度自律，注重细节，守承诺"},
                "外倾性": {"low": "偏内向，喜欢独处或小范围社交", "medium": "内外向均衡，社交适度", "high": "偏外向，喜欢社交，活跃"},
                "宜人性": {"low": "较为独立，注重自我", "medium": "友善但有原则", "high": "极度友善，乐于助人"},
                "神经质": {"low": "情绪极稳定，不易受外界影响", "medium": "情绪稳定性一般", "high": "情绪较敏感，易受外界影响"}
            }
            return desc_map.get(dimension, {}).get(level, "")

        dimensions = [
            {"dimension": "开放性", "score": openness_score, "level": get_level(openness_score)[0]},
            {"dimension": "责任心", "score": conscientiousness_score, "level": get_level(conscientiousness_score)[0]},
            {"dimension": "外倾性", "score": extraversion_score, "level": get_level(extraversion_score)[0]},
            {"dimension": "宜人性", "score": agreeableness_score, "level": get_level(agreeableness_score)[0]},
            {"dimension": "神经质", "score": neuroticism_score, "level": get_level(neuroticism_score)[0]}
        ]

        dimension_descs = []
        for d in dimensions:
            level, level_text = get_level(d["score"])
            desc = get_dimension_desc(d["dimension"], d["score"], level, level_text)
            dimension_descs.append({
                "dimension": d["dimension"],
                "score": d["score"],
                "max_score": 20,  # 每个维度4题×5分
                "level": level,
                "description": desc
            })

        return {
            "total_score": None,  # 大五人格没有总分
            "dimension_scores": dimension_descs,
            "result_level": "personality",
            "result_title": "大五人格测试结果",
            "result_description": "您的人格特质各维度表现如下"
        }

    @staticmethod
    def _calculate_stress_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算工作生活压力量表分数"""
        # 工作/学习压力: 第1,4,7,10,13,16,19题
        work_questions = [1, 4, 7, 10, 13, 16, 19]
        # 生活压力: 第2,5,8,11,14,17题
        life_questions = [2, 5, 8, 11, 14, 17]
        # 人际关系压力: 第3,6,9,12,15,18,20题
        relationship_questions = [3, 6, 9, 12, 15, 18, 20]

        work_score = sum(answers.get(q, 1) for q in work_questions)
        life_score = sum(answers.get(q, 1) for q in life_questions)
        relationship_score = sum(answers.get(q, 1) for q in relationship_questions)
        total_score = work_score + life_score + relationship_score

        # 结果等级判定
        if total_score <= 30:
            level = "none"
            title = "无压力"
            description = "整体状态轻松，各方面无明显压力，身心状态良好"
        elif total_score <= 45:
            level = "mild"
            title = "轻微压力"
            description = "偶尔出现压力表现，可通过自我调节（如运动、休息）快速缓解"
        elif total_score <= 60:
            level = "moderate"
            title = "中度压力"
            description = "频繁感受到压力，对日常工作/生活有一定影响，需通过合理的方式疏导压力"
        else:
            level = "severe"
            title = "重度压力"
            description = "长期处于高压状态，身心俱疲，严重影响工作/生活与人际关系，建议寻求心理疏导与压力调节指导"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "工作/学习压力", "score": work_score, "max_score": 28, "level": level},
                {"dimension": "生活压力", "score": life_score, "max_score": 24, "level": level},
                {"dimension": "人际关系压力", "score": relationship_score, "max_score": 28, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_ses_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算自尊量表(SES)分数"""
        # 反向题: 2, 5, 6, 8, 9
        reverse_questions = [2, 5, 6, 8, 9]

        total_score = 0
        for q in range(1, 11):
            value = answers.get(q, 2)
            if q in reverse_questions:
                total_score += TestService._reverse_score(value, 4)
            else:
                total_score += value

        # 结果等级判定
        if total_score >= 30:
            level = "high"
            title = "高自尊"
            description = "自我价值感强，自信且自我接纳程度高"
        elif total_score >= 20:
            level = "medium"
            title = "中等自尊"
            description = "自我价值感一般，有一定自信，偶有自我怀疑"
        else:
            level = "low"
            title = "低自尊"
            description = "自我价值感较低，缺乏自信，需要提升自我接纳"

        return {
            "total_score": total_score,
            "dimension_scores": [],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_lsas_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算社交焦虑量表(LSAS)分数"""
        # 恐惧维度: 奇数题
        fear_questions = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        # 回避维度: 偶数题
        avoidance_questions = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

        fear_score = sum(answers.get(q, 1) for q in fear_questions)
        avoidance_score = sum(answers.get(q, 1) for q in avoidance_questions)
        total_score = fear_score + avoidance_score

        # 结果等级判定
        if total_score <= 30:
            level = "none"
            title = "无明显社交焦虑"
            description = "社交场合无明显焦虑，能够正常社交"
        elif total_score <= 50:
            level = "mild"
            title = "轻度社交焦虑"
            description = "在某些社交场合有轻微焦虑，不影响正常社交"
        elif total_score <= 65:
            level = "moderate"
            title = "中度社交焦虑"
            description = "在多数社交场合有明显焦虑，有一定回避行为"
        else:
            level = "severe"
            title = "重度社交焦虑"
            description = "在社交场合有严重焦虑，强烈回避社交，建议寻求专业帮助"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "恐惧", "score": fear_score, "max_score": 40, "level": level},
                {"dimension": "回避", "score": avoidance_score, "max_score": 40, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_emotional_stability_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算情绪稳定性量表分数"""
        # 反向题: 1, 4, 6, 9, 11, 13, 15
        reverse_questions = [1, 4, 6, 9, 11, 13, 15]

        total_score = 0
        for q in range(1, 16):
            value = answers.get(q, 3)
            if q in reverse_questions:
                total_score += TestService._reverse_score(value, 5)
            else:
                total_score += value

        # 结果等级判定
        if total_score >= 60:
            level = "high"
            title = "情绪非常稳定"
            description = "情绪调节能力强，不易受外界影响，能够保持平和心态"
        elif total_score >= 45:
            level = "medium_high"
            title = "情绪较稳定"
            description = "情绪调节能力较强，偶有波动但能快速恢复"
        elif total_score >= 30:
            level = "medium_low"
            title = "情绪稳定性一般"
            description = "情绪波动较明显，需要提升情绪管理能力"
        else:
            level = "low"
            title = "情绪不稳定"
            description = "情绪波动大，易受外界影响，建议学习情绪调节技巧"

        return {
            "total_score": total_score,
            "dimension_scores": [],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_burnout_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算职业倦怠量表(MBI)分数"""
        # 情绪衰竭: 1-5题
        exhaustion_questions = [1, 2, 3, 4, 5]
        # 去人格化: 6-10题
        depersonalization_questions = [6, 7, 8, 9, 10]
        # 个人成就感: 11-15题（反向题）
        achievement_questions = [11, 12, 13, 14, 15]

        exhaustion_score = sum(answers.get(q, 1) for q in exhaustion_questions)
        depersonalization_score = sum(answers.get(q, 1) for q in depersonalization_questions)
        # 个人成就感需要反向计分
        achievement_score = sum(TestService._reverse_score(answers.get(q, 4), 7) for q in achievement_questions)
        total_score = exhaustion_score + depersonalization_score + achievement_score

        # 结果等级判定（总分越高，倦怠越严重）
        if total_score <= 35:
            level = "none"
            title = "无职业倦怠"
            description = "工作状态良好，无明显倦怠表现"
        elif total_score <= 60:
            level = "mild"
            title = "轻度倦怠"
            description = "偶尔感到工作疲惫，需要适当休息和调整"
        elif total_score <= 85:
            level = "moderate"
            title = "中度倦怠"
            description = "经常感到工作疲惫，对工作有疏离感，需要关注工作与生活的平衡"
        else:
            level = "severe"
            title = "重度倦怠"
            description = "严重职业倦怠，情绪耗竭，建议寻求职业咨询和心理支持"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "情绪衰竭", "score": exhaustion_score, "max_score": 35, "level": level},
                {"dimension": "去人格化", "score": depersonalization_score, "max_score": 35, "level": level},
                {"dimension": "个人成就感", "score": achievement_score, "max_score": 35, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def _calculate_sleep_score(answers: Dict[int, int], scoring_rules: Dict) -> Dict[str, Any]:
        """计算匹茨堡睡眠质量指数(PSQI)分数"""
        # PSQI采用加权计分，这里使用简化版计分
        # 主要问题题目：5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17（睡眠障碍和日间功能障碍）
        sleep_problem_questions = [5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        sleep_quality_questions = [2, 6, 17]  # 入睡时间、主观睡眠质量、日间功能障碍
        sleep_time_questions = [1, 3, 4]  # 上床时间、起床时间、睡眠时长

        # 计算各维度得分
        problem_score = sum(answers.get(q, 0) for q in sleep_problem_questions)
        quality_score = sum(answers.get(q, 0) for q in sleep_quality_questions)
        time_score = sum(answers.get(q, 0) for q in sleep_time_questions)

        # 简化版总分计算
        total_score = problem_score + quality_score + (time_score // 2)

        # 结果等级判定（PSQI总分越高，睡眠质量越差）
        if total_score <= 5:
            level = "good"
            title = "睡眠质量很好"
            description = "睡眠质量优秀，保持良好作息"
        elif total_score <= 10:
            level = "fair"
            title = "睡眠质量尚可"
            description = "睡眠质量一般，偶尔有睡眠问题"
        else:
            level = "poor"
            title = "睡眠质量差"
            description = "存在明显睡眠问题，建议改善睡眠习惯或寻求专业帮助"

        return {
            "total_score": total_score,
            "dimension_scores": [
                {"dimension": "睡眠问题", "score": problem_score, "max_score": 36, "level": level},
                {"dimension": "主观质量", "score": quality_score, "max_score": 9, "level": level},
                {"dimension": "睡眠时间", "score": time_score, "max_score": 9, "level": level}
            ],
            "result_level": level,
            "result_title": title,
            "result_description": description
        }

    @staticmethod
    def submit_test(db: Session, user_id: int, test_id: int, request: SubmitTestRequest, save_record: bool = True) -> Optional[TestResult]:
        """提交测试并计算结果"""
        # 获取测试信息
        test = db.query(PsychologicalTest).filter(
            PsychologicalTest.id == test_id
        ).first()

        if not test:
            return None

        # 根据测试类型计算分数
        result_data = None
        if test.test_code == "SAS20":
            result_data = TestService._calculate_sas_score(request.answers, test.scoring_rules)
        elif test.test_code == "SDS20":
            result_data = TestService._calculate_sds_score(request.answers, test.scoring_rules)
        elif test.test_code == "BIG5_20":
            result_data = TestService._calculate_big5_score(request.answers, test.scoring_rules)
        elif test.test_code == "STRESS20":
            result_data = TestService._calculate_stress_score(request.answers, test.scoring_rules)
        elif test.test_code == "SES10":
            result_data = TestService._calculate_ses_score(request.answers, test.scoring_rules)
        elif test.test_code == "LSAS20":
            result_data = TestService._calculate_lsas_score(request.answers, test.scoring_rules)
        elif test.test_code == "ES15":
            result_data = TestService._calculate_emotional_stability_score(request.answers, test.scoring_rules)
        elif test.test_code == "MBI15":
            result_data = TestService._calculate_burnout_score(request.answers, test.scoring_rules)
        elif test.test_code == "PSQI19":
            result_data = TestService._calculate_sleep_score(request.answers, test.scoring_rules)
        else:
            # 通用计分（简单求和）
            total_score = sum(request.answers.values())
            result_data = {
                "total_score": total_score,
                "dimension_scores": [],
                "result_level": "unknown",
                "result_title": "测试完成",
                "result_description": "感谢您的参与"
            }

        # 生成建议
        suggestions = TestService._generate_suggestions(test.test_code, result_data)

        # 创建结果记录
        result = TestResult(
            user_id=user_id,
            test_id=test_id,
            answers=request.answers,
            total_score=result_data.get("total_score"),
            dimension_scores=result_data.get("dimension_scores"),
            result_level=result_data.get("result_level"),
            result_title=result_data.get("result_title"),
            result_description=result_data.get("result_description"),
            suggestions=suggestions
        )

        if save_record:
            db.add(result)
            db.flush()  # 先flush以获得result.id
        else:
            # 即使不保存到用户历史，仍写入数据库并标记为删除（用于数据追溯）
            result.is_deleted = True
            db.add(result)
            db.flush()

        # 生成AI建议（异步，不阻塞用户）
        try:
            ai_suggestion = TestService._generate_ai_suggestion(
                db, result, test, result_data
            )
            result.ai_suggestion = ai_suggestion
        except Exception as e:
            # AI生成失败不影响测试保存
            print(f"AI建议生成失败: {e}")
            import traceback
            traceback.print_exc()

        # 删除进度记录
        db.query(TestProgress).filter(
            and_(
                TestProgress.user_id == user_id,
                TestProgress.test_id == test_id
            )
        ).delete()

        db.commit()
        db.refresh(result)

        # 附加测试信息
        result.test_code = test.test_code
        result.test_title = test.title

        return result

    @staticmethod
    def _generate_suggestions(test_code: str, result_data: Dict) -> str:
        """生成建议"""
        level = result_data.get("result_level", "")

        general_suggestions = {
            "none": "保持良好的生活习惯，继续维持积极的心态。",
            "mild": "建议适当放松身心，可通过运动、音乐、社交等方式缓解压力。",
            "moderate": "建议关注心理健康状况，可通过正念冥想、规律作息等方式调节，必要时寻求专业心理疏导。",
            "severe": "建议及时寻求专业心理咨询师的帮助，进行系统的心理评估与辅导。",
            "personality": "了解自己的人格特质有助于更好地发挥优势、改善不足。",
            "high": "继续保持积极的心态和健康的生活方式。",
            "medium": "建议关注自我提升，增强自信和自我接纳。",
            "low": "建议通过积极的自我对话、设定小目标等方式逐步提升。",
            "good": "继续保持良好的睡眠习惯，规律作息。",
            "fair": "建议改善睡眠卫生，避免睡前使用电子设备，保持安静舒适的睡眠环境。",
            "poor": "建议建立规律的睡眠时间表，避免咖啡因和午睡，必要时咨询睡眠专家。"
        }

        suggestion = general_suggestions.get(level, general_suggestions.get("mild", ""))

        # 根据测试类型添加特定建议
        if test_code == "SAS20":
            if level in ["moderate", "severe"]:
                suggestion += "\n\n焦虑症状明显时，可尝试深呼吸练习、渐进式肌肉放松等技巧。"
        elif test_code == "SDS20":
            if level in ["moderate", "severe"]:
                suggestion += "\n\n抑郁情绪持续时，建议保持社交活动，避免自我封闭，必要时就医。"
        elif test_code == "STRESS20":
            suggestion += "\n\n压力管理建议：合理规划时间，学会拒绝，保持工作生活平衡。"
        elif test_code == "SES10":
            if level == "low":
                suggestion += "\n\n建议通过积极的自我对话、记录成就、设定可实现的目标等方式提升自尊。"
        elif test_code == "LSAS20":
            if level in ["moderate", "severe"]:
                suggestion += "\n\n社交焦虑明显时，可尝试系统脱敏法、认知行为疗法等技术，逐步提升社交自信。"
        elif test_code == "ES15":
            if level in ["medium_low", "low"]:
                suggestion += "\n\n情绪管理技巧：正念冥想、运动、写日记、寻求社交支持等都有助于提升情绪稳定性。"
        elif test_code == "MBI15":
            if level in ["moderate", "severe"]:
                suggestion += "\n\n职业倦怠应对：合理安排工作和休息时间，培养工作外的兴趣爱好，必要时寻求职业咨询。"
        elif test_code == "PSQI19":
            if level in ["fair", "poor"]:
                suggestion += "\n\n睡眠改善建议：保持规律作息，避免睡前使用电子设备，创造舒适的睡眠环境，限制咖啡因摄入。"

        return suggestion

    @staticmethod
    def _generate_ai_suggestion(
        db: Session,
        result: TestResult,
        test: PsychologicalTest,
        result_data: Dict
    ) -> Optional[str]:
        """
        生成AI个性化建议

        Args:
            db: 数据库会话
            result: 测试结果对象
            test: 测试对象
            result_data: 结果数据

        Returns:
            str: AI生成的建议
        """
        try:
            ai_service = AIService()

            # 构建维度信息
            dimension_info = ""
            if result.dimension_scores and len(result.dimension_scores) > 0:
                dimension_info = "\n【各维度得分】\n"
                for dim in result.dimension_scores:
                    level_mapping = {
                        'none': '正常',
                        'mild': '轻度',
                        'moderate': '中度',
                        'severe': '重度'
                    }
                    level_text = level_mapping.get(dim.get('level', ''), dim.get('level', ''))
                    dimension_info += f"- {dim.get('dimension', '未知维度')}: {dim.get('score', 0)}分（{level_text}）\n"

            # 构建prompt
            level_text = result_data.get("result_level", "")
            level_display = {
                'none': '正常',
                'mild': '轻度',
                'moderate': '中度',
                'severe': '重度'
            }.get(level_text, level_text)

            prompt = f"""你是一位温暖、专业的心理咨询师"小宁"。用户刚刚完成了【{test.title}】测试，以下是用户的测试结果：

【测试得分】：{result.total_score}分
【测试等级】：{level_display}

{dimension_info}

请根据这个结果，为用户提供一段温暖、专业的建议（100-150字）：

1. 首先给予用户共情和肯定
2. 用通俗易懂的语言简要说明当前状态的含义
3. 给出1-2个具体、可操作的改善建议
4. 用鼓励的话语结束

要求：
- 语气温和、友善，不带评判色彩
- 避免使用过于专业的术语
- 不要进行疾病诊断，只提供建议
- 如果结果为"重度"，请温和地建议寻求专业帮助
- 保持积极和支持的态度

请直接给出建议文本，不要加任何标题或说明："""

            messages = [{"role": "user", "content": prompt}]

            # 调用AI生成建议
            ai_suggestion = ai_service.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            # 清理AI返回的内容
            ai_suggestion = ai_suggestion.strip()
            if ai_suggestion.startswith('"') and ai_suggestion.endswith('"'):
                ai_suggestion = ai_suggestion[1:-1]

            return ai_suggestion

        except Exception as e:
            print(f"AI建议生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def get_test_result(db: Session, result_id: int, user_id: int) -> Optional[TestResult]:
        """获取测试结果"""
        result = db.query(TestResult).filter(
            and_(
                TestResult.id == result_id,
                TestResult.user_id == user_id
            )
        ).first()

        if result:
            # 附加测试信息
            test = db.query(PsychologicalTest).filter(PsychologicalTest.id == result.test_id).first()
            if test:
                result.test_code = test.test_code
                result.test_title = test.title

        return result

    @staticmethod
    def get_test_history(db: Session, user_id: int, test_id: Optional[int] = None,
                        page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取用户测试历史"""
        q = db.query(TestResult).filter(
            TestResult.user_id == user_id,
            TestResult.is_deleted == False
        )

        if test_id:
            q = q.filter(TestResult.test_id == test_id)

        # 按时间倒序
        q = q.order_by(desc(TestResult.created_at))

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        results = q.offset(offset).limit(page_size).all()

        # 附加测试信息
        for result in results:
            test = db.query(PsychologicalTest).filter(PsychologicalTest.id == result.test_id).first()
            if test:
                result.test_code = test.test_code
                result.test_title = test.title
                result._total_questions = test.total_questions
                result._option_type = test.option_type

        return {
            "total": total,
            "items": results
        }

    @staticmethod
    def get_test_trend(db: Session, user_id: int, test_id: int) -> Optional[Dict[str, Any]]:
        """获取测试趋势数据"""
        test = db.query(PsychologicalTest).filter(PsychologicalTest.id == test_id).first()
        if not test:
            return None

        # 获取该用户在该测试下的所有结果，按时间正序
        results = db.query(TestResult).filter(
            and_(
                TestResult.user_id == user_id,
                TestResult.test_id == test_id
            )
        ).order_by(TestResult.created_at).all()

        # 转换为趋势数据点
        trend_data = []
        for result in results:
            if result.total_score is not None:
                trend_data.append({
                    "date": result.created_at.strftime("%Y-%m-%d"),
                    "score": result.total_score
                })

        return {
            "test_id": test_id,
            "test_code": test.test_code,
            "test_title": test.title,
            "trend_data": trend_data
        }

    @staticmethod
    def toggle_favorite(db: Session, result_id: int, user_id: int) -> Optional[TestResult]:
        """收藏/取消收藏结果"""
        result = db.query(TestResult).filter(
            and_(
                TestResult.id == result_id,
                TestResult.user_id == user_id
            )
        ).first()

        if result:
            result.is_favorite = not result.is_favorite
            db.commit()
            db.refresh(result)

            # 附加测试信息
            test = db.query(PsychologicalTest).filter(PsychologicalTest.id == result.test_id).first()
            if test:
                result.test_code = test.test_code
                result.test_title = test.title

        return result

    @staticmethod
    def add_favorite(db: Session, result_id: int, user_id: int) -> Optional[TestResult]:
        """收藏结果（幂等）"""
        result = db.query(TestResult).filter(
            and_(
                TestResult.id == result_id,
                TestResult.user_id == user_id
            )
        ).first()

        if result:
            result.is_favorite = True
            db.commit()
            db.refresh(result)

            test = db.query(PsychologicalTest).filter(PsychologicalTest.id == result.test_id).first()
            if test:
                result.test_code = test.test_code
                result.test_title = test.title

        return result

    @staticmethod
    def remove_favorite(db: Session, result_id: int, user_id: int) -> Optional[TestResult]:
        """取消收藏（幂等）"""
        result = db.query(TestResult).filter(
            and_(
                TestResult.id == result_id,
                TestResult.user_id == user_id
            )
        ).first()

        if result:
            result.is_favorite = False
            db.commit()
            db.refresh(result)

            test = db.query(PsychologicalTest).filter(PsychologicalTest.id == result.test_id).first()
            if test:
                result.test_code = test.test_code
                result.test_title = test.title

        return result

    @staticmethod
    def delete_test_result(db: Session, result_id: int, user_id: int) -> bool:
        """
        软删除测试结果

        Args:
            db: 数据库会话
            result_id: 结果ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        result = db.query(TestResult).filter(
            and_(
                TestResult.id == result_id,
                TestResult.user_id == user_id,
                TestResult.is_deleted == False
            )
        ).first()

        if not result:
            raise ValueError("测试结果不存在")

        result.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def get_progress(db: Session, user_id: int, test_id: int) -> Optional[TestProgress]:
        """获取答题进度"""
        return db.query(TestProgress).filter(
            and_(
                TestProgress.user_id == user_id,
                TestProgress.test_id == test_id
            )
        ).first()

    # ==================== 管理后台方法 ====================

    @staticmethod
    def get_admin_tests(
        db: Session,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取心理测试列表（管理后台）

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            包含测试列表和总数的字典
        """
        # 构建查询
        q = db.query(PsychologicalTest)

        # 关键词搜索
        if keyword:
            q = q.filter(
                or_(
                    PsychologicalTest.title.contains(keyword),
                    PsychologicalTest.description.contains(keyword),
                    PsychologicalTest.test_code.contains(keyword)
                )
            )

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        tests = q.order_by(desc(PsychologicalTest.created_at)).offset(offset).limit(page_size).all()

        # 为每个测试添加统计信息
        items = []
        for test in tests:
            # 统计题目数量
            question_count = db.query(TestQuestion).filter(
                TestQuestion.test_id == test.id
            ).count()

            # 统计完成次数
            completed_count = db.query(TestResult).filter(
                and_(
                    TestResult.test_id == test.id,
                    TestResult.is_deleted == False
                )
            ).count()

            items.append({
                "id": test.id,
                "title": test.title,
                "test_code": test.test_code,
                "category": test.category,
                "description": test.description,
                "questionCount": question_count,
                "completedCount": completed_count,
                "createTime": test.created_at.strftime("%Y-%m-%d %H:%M:%S") if test.created_at else "",
                "isActive": test.is_active
            })

        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size
        }

    @staticmethod
    def get_admin_test_detail(db: Session, test_id: int) -> Optional[Dict[str, Any]]:
        """
        获取测试详情（管理后台）

        Args:
            db: 数据库会话
            test_id: 测试ID

        Returns:
            包含测试完整信息的字典
        """
        test = db.query(PsychologicalTest).filter(PsychologicalTest.id == test_id).first()

        if not test:
            return None

        # 获取题目列表
        questions = db.query(TestQuestion).filter(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.question_number).all()

        question_list = []
        for q in questions:
            question_list.append({
                "id": q.id,
                "questionNumber": q.question_number,
                "questionText": q.question_text,
                "options": q.options,
                "dimension": q.dimension,
                "isReverse": q.is_reverse
            })

        return {
            "id": test.id,
            "testCode": test.test_code,
            "title": test.title,
            "description": test.description,
            "category": test.category,
            "introText": test.intro_text,
            "totalQuestions": test.total_questions,
            "optionType": test.option_type,
            "scoringRules": test.scoring_rules,
            "hotValue": test.hot_value,
            "coverImage": test.cover_image,
            "isActive": test.is_active,
            "questions": question_list,
            "createTime": test.created_at.strftime("%Y-%m-%d %H:%M:%S") if test.created_at else ""
        }

    @staticmethod
    def get_test_questions(db: Session, test_id: int) -> List[Dict[str, Any]]:
        """
        获取测试的所有题目

        Args:
            db: 数据库会话
            test_id: 测试ID

        Returns:
            题目列表
        """
        questions = db.query(TestQuestion).filter(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.question_number).all()

        return [
            {
                "id": q.id,
                "questionNumber": q.question_number,
                "questionText": q.question_text,
                "options": q.options,
                "dimension": q.dimension,
                "isReverse": q.is_reverse
            }
            for q in questions
        ]

    @staticmethod
    def delete_test(db: Session, test_id: int) -> bool:
        """
        删除心理测试（软删除）

        Args:
            db: 数据库会话
            test_id: 测试ID

        Returns:
            是否删除成功
        """
        test = db.query(PsychologicalTest).filter(PsychologicalTest.id == test_id).first()

        if not test:
            raise ValueError("测试不存在")

        # 软删除：设置 is_active 为 False
        test.is_active = False
        db.commit()

        return True

    @staticmethod
    def generate_comprehensive_analysis(db: Session, user_id: int, days: int = 90) -> Optional[Dict[str, Any]]:
        """
        生成综合心理分析报告

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 分析最近多少天的数据（默认90天）

        Returns:
            包含分析报告的字典
        """
        try:
            # 1. 获取用户信息
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # 2. 计算时间范围
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days)

            # 3. 获取近期所有测试结果（未删除的）
            recent_results = db.query(TestResult).filter(
                and_(
                    TestResult.user_id == user_id,
                    TestResult.is_deleted == False,
                    TestResult.created_at >= cutoff_date
                )
            ).order_by(desc(TestResult.created_at)).all()

            if not recent_results:
                return {
                    "error": "近期无测试记录",
                    "message": f"最近{days}天内没有找到测试记录，请先完成一些心理测试后再生成分析报告。"
                }

            # 4. 整理测试数据
            test_summary = []
            test_by_category = {}

            for result in recent_results:
                test = db.query(PsychologicalTest).filter(
                    PsychologicalTest.id == result.test_id
                ).first()

                if test:
                    category = test.category or "other"

                    test_info = {
                        "test_code": test.test_code,
                        "test_title": test.title,
                        "category": category,
                        "total_score": result.total_score,
                        "result_level": result.result_level,
                        "result_title": result.result_title,
                        "result_description": result.result_description,
                        "dimension_scores": result.dimension_scores,
                        "completed_at": result.created_at.strftime("%Y-%m-%d")
                    }

                    test_summary.append(test_info)

                    # 按分类汇总（取最近一次）
                    if category not in test_by_category:
                        test_by_category[category] = test_info

            # 5. 计算用户年龄
            age = None
            if user.birth_date:
                today = datetime.now().date()
                birth_date = user.birth_date
                age = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
                )

            # 6. 调用AI生成综合分析
            ai_service = AIService()
            analysis_report = TestService._generate_ai_analysis_report(
                ai_service,
                user,
                age,
                test_summary,
                test_by_category,
                days
            )

            return {
                "user_info": {
                    "nickname": user.nickname,
                    "gender": user.gender,
                    "age": age,
                    "bio": user.bio
                },
                "analysis_period": {
                    "days": days,
                    "test_count": len(recent_results),
                    "earliest_test": recent_results[-1].created_at.strftime("%Y-%m-%d"),
                    "latest_test": recent_results[0].created_at.strftime("%Y-%m-%d")
                },
                "test_summary": test_summary,
                "ai_analysis": analysis_report,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            print(f"生成综合分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": "生成失败",
                "message": f"生成分析报告时出错: {str(e)}"
            }

    @staticmethod
    def _generate_ai_analysis_report(
        ai_service: AIService,
        user: User,
        age: Optional[int],
        test_summary: List[Dict],
        test_by_category: Dict,
        days: int
    ) -> str:
        """
        使用AI生成综合分析报告

        Args:
            ai_service: AI服务实例
            user: 用户对象
            age: 用户年龄
            test_summary: 测试摘要列表
            test_by_category: 按分类的测试数据
            days: 分析天数

        Returns:
            AI生成的分析报告文本
        """
        # 构建用户信息描述
        user_info = f"""【用户基本信息】
- 昵称：{user.nickname or '未设置'}
- 性别：{'男' if user.gender == 'male' else '女' if user.gender == 'female' else '未设置'}
- 年龄：{age}岁（{user.birth_date.strftime('%Y-%m-%d') if user.birth_date else '未设置'}）
- 个人简介：{user.bio or '无'}"""

        # 构建测试记录摘要
        test_info = f"\n\n【近期测试记录】（最近{days}天，共{len(test_summary)}次）\n"

        # 按分类展示测试结果
        category_order = ['anxiety', 'depression', 'stress', 'personality', 'sleep']
        category_names = {
            'anxiety': '焦虑',
            'depression': '抑郁',
            'stress': '压力',
            'personality': '人格',
            'sleep': '睡眠',
            'other': '其他'
        }

        for category in category_order:
            if category in test_by_category:
                test = test_by_category[category]
                level_text = {
                    'none': '正常',
                    'mild': '轻度',
                    'moderate': '中度',
                    'severe': '重度',
                    'high': '高',
                    'medium': '中等',
                    'low': '低',
                    'good': '良好',
                    'fair': '一般',
                    'poor': '较差'
                }.get(test.get('result_level', ''), test.get('result_level', ''))

                test_info += f"""
【{category_names.get(category, category)}测试】
- 测试：{test['test_title']}
- 得分：{test['total_score']}分（{level_text}）
- 结果：{test['result_title']}
- 测试时间：{test['completed_at']}"""

                # 添加维度得分
                if test.get('dimension_scores'):
                    test_info += "\n- 各维度得分："
                    for dim in test['dimension_scores']:
                        test_info += f"\n  · {dim.get('dimension', '未知')}：{dim.get('score', 0)}分"

        # 添加其他分类
        for category, test in test_by_category.items():
            if category not in category_order:
                level_text = {
                    'none': '正常',
                    'mild': '轻度',
                    'moderate': '中度',
                    'severe': '重度'
                }.get(test.get('result_level', ''), test.get('result_level', ''))

                test_info += f"""
【{category_names.get(category, category)}测试】
- 测试：{test['test_title']}
- 得分：{test['total_score']}分（{level_text}）
- 结果：{test['result_title']}
- 测试时间：{test['completed_at']}"""

        # 构建AI Prompt
        prompt = f"""你是一位温暖、专业的心理咨询师"小宁"。用户请求生成一份综合心理分析报告。

{user_info}
{test_info}

请根据以上信息，为用户生成一份全面、温暖、专业的心理分析报告，包含以下内容：

## 📊 整体心理状况评估
对用户当前的心理状况进行整体评估（100-150字）

## 🔍 各维度详细分析
分析用户在焦虑、抑郁、压力等各维度的表现（200-250字）

## 📈 心理状况趋势与建议
根据测试结果，给出具体的改善建议（250-300字），包括：
- 生活方式调整建议
- 情绪管理技巧
- 是否需要寻求专业帮助的建议

## 💪 积极特质与优势
肯定用户在心理健康方面的积极面（50-100字）

要求：
- 语气温和、友善，不带评判色彩
- 使用通俗易懂的语言，避免专业术语
- 每个部分用emoji图标开头
- 用加粗标注重点内容
- 保持积极和支持的态度
- 如果出现重度指标，温和地建议寻求专业帮助
- 总字数控制在600-800字

请直接生成报告文本："""

        messages = [{"role": "user", "content": prompt}]

        # 调用AI生成报告
        ai_report = ai_service.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return ai_report.strip()
