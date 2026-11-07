"""
心理测试相关模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PsychologicalTest(Base):
    """心理测试问卷表"""
    __tablename__ = "psychological_tests"

    id = Column(BigInteger, primary_key=True, index=True, comment="测试ID")
    test_code = Column(String(50), unique=True, nullable=False, index=True, comment="测试代码(如SAS20)")
    title = Column(String(200), nullable=False, comment="测试标题")
    description = Column(Text, comment="测试描述")
    category = Column(String(50), comment="测试分类: anxiety/depression/personality/stress")
    intro_text = Column(Text, comment="测试说明文字")
    total_questions = Column(Integer, default=0, comment="总题数")
    score_type = Column(String(20), default="total", comment="计分类型: total=总分, dimension=维度分")
    option_type = Column(String(20), default="4选项", comment="选项类型: 4选项/5选项")

    # 计分规则存储为JSON
    scoring_rules = Column(JSON, comment="计分规则配置")
    result_rules = Column(JSON, comment="结果等级解读规则")

    # 排序和显示
    sort_order = Column(Integer, default=0, comment="排序序号")
    is_active = Column(Boolean, default=True, comment="是否启用")
    hot_value = Column(Integer, default=0, comment="热度值")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PsychologicalTest(id={self.id}, title={self.title}, code={self.test_code})>"


class TestQuestion(Base):
    """测试题目表"""
    __tablename__ = "test_questions"

    id = Column(BigInteger, primary_key=True, index=True, comment="题目ID")
    test_id = Column(BigInteger, ForeignKey("psychological_tests.id", ondelete="CASCADE"), nullable=False, comment="所属测试ID")
    question_number = Column(Integer, nullable=False, comment="题目序号")
    question_text = Column(Text, nullable=False, comment="题目内容")

    # 选项配置 (存储为JSON数组)
    # [{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}]
    options = Column(JSON, nullable=False, comment="选项配置")

    # 计分相关
    dimension = Column(String(50), comment="所属维度")
    is_reverse = Column(Boolean, default=False, comment="是否反向题")
    reverse_value = Column(Integer, comment="反向计分值配置")

    sort_order = Column(Integer, default=0, comment="排序序号")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联关系
    test = relationship("PsychologicalTest", back_populates="questions")

    def __repr__(self):
        return f"<TestQuestion(id={self.id}, number={self.question_number}, text={self.question_text[:20]})>"


class TestResult(Base):
    """用户测试结果表"""
    __tablename__ = "test_results"

    id = Column(BigInteger, primary_key=True, index=True, comment="结果ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    questionnaire_id = Column(BigInteger, ForeignKey("psychological_tests.id", ondelete="CASCADE"), nullable=True, index=True, comment="问卷ID（旧字段）")
    test_id = Column(BigInteger, ForeignKey("psychological_tests.id", ondelete="CASCADE"), nullable=True, index=True, comment="测试ID")

    # 答题记录 (存储为JSON: {question_number: option_value})
    answers = Column(JSON, nullable=False, comment="答题记录")

    # 计分结果
    total_score = Column(Integer, comment="总得分")
    dimension_scores = Column(JSON, comment="各维度得分")

    # 结果解读
    result_level = Column(String(50), comment="结果等级: none/mild/moderate/severe")
    result_title = Column(String(100), comment="结果标题")
    result_description = Column(Text, comment="结果描述")
    suggestions = Column(Text, comment="建议内容")

    # AI 生成建议 (可选)
    ai_suggestion = Column(Text, comment="AI生成的个性化建议")

    # 状态
    is_favorited = Column(Boolean, default=False, comment="是否收藏")
    is_favorite = Column(Boolean, default=False, comment="是否收藏（兼容字段）")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    completed_at = Column(DateTime, server_default=func.now(), index=True, comment="完成时间")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")

    def __repr__(self):
        return f"<TestResult(id={self.id}, user_id={self.user_id}, test_id={self.test_id}, score={self.total_score})>"


class TestProgress(Base):
    """用户答题进度表"""
    __tablename__ = "test_progress"

    id = Column(BigInteger, primary_key=True, index=True, comment="进度ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    test_id = Column(BigInteger, ForeignKey("psychological_tests.id", ondelete="CASCADE"), nullable=False, index=True, comment="测试ID")

    # 已答题记录 (存储为JSON: {question_number: option_value})
    answers = Column(JSON, default={}, comment="已答题目记录")

    current_question = Column(Integer, default=1, comment="当前答题进度")

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<TestProgress(id={self.id}, user_id={self.user_id}, test_id={self.test_id})>"
