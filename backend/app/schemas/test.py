"""
心理测试相关 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== 请求 Schemas ====================

class TestListQuery(BaseModel):
    """测试列表查询参数"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="分类筛选: anxiety/depression/personality/stress")
    sort: Optional[str] = Field("latest", description="排序方式: hot/latest/rating")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class StartTestRequest(BaseModel):
    """开始测试请求"""
    test_id: int = Field(..., description="测试ID")


class SaveProgressRequest(BaseModel):
    """保存答题进度请求"""
    answers: Dict[int, int] = Field(..., description="答题记录: {题目序号: 选项值}")


class SubmitTestRequest(BaseModel):
    """提交测试请求"""
    answers: Dict[int, int] = Field(..., description="答题记录: {题目序号: 选项值}")


class FavoriteResultRequest(BaseModel):
    """收藏结果请求"""
    result_id: int = Field(..., description="结果ID")


class GetTrendRequest(BaseModel):
    """获取趋势数据请求"""
    test_id: int = Field(..., description="测试ID")


# ==================== 响应 Schemas ====================

class OptionSchema(BaseModel):
    """选项 Schema"""
    value: int
    label: str

    class Config:
        from_attributes = True


class QuestionSchema(BaseModel):
    """题目 Schema"""
    id: int
    question_number: int
    question_text: str
    options: List[OptionSchema]
    dimension: Optional[str] = None
    is_reverse: bool = False

    class Config:
        from_attributes = True


class TestListItemSchema(BaseModel):
    """测试列表项 Schema"""
    id: int
    test_code: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    intro_text: Optional[str] = None
    total_questions: int
    option_type: str
    hot_value: int

    class Config:
        from_attributes = True


class TestDetailSchema(BaseModel):
    """测试详情 Schema"""
    id: int
    test_code: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    intro_text: Optional[str] = None
    total_questions: int
    score_type: str
    option_type: str
    scoring_rules: Optional[Dict[str, Any]] = None
    result_rules: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class StartTestResponseSchema(BaseModel):
    """开始测试响应 Schema"""
    test_id: int
    test_code: str
    title: str
    intro_text: Optional[str] = None
    option_type: str
    questions: List[QuestionSchema]


class DimensionScoreSchema(BaseModel):
    """维度得分 Schema"""
    dimension: str
    score: int
    level: str


class TestResultSchema(BaseModel):
    """测试结果 Schema"""
    id: int
    test_id: int
    test_code: Optional[str] = None
    test_title: Optional[str] = None
    total_score: Optional[int] = None
    dimension_scores: Optional[List[DimensionScoreSchema]] = None
    result_level: Optional[str] = None
    result_title: Optional[str] = None
    result_description: Optional[str] = None
    suggestions: Optional[str] = None
    ai_suggestion: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TestHistoryItemSchema(BaseModel):
    """测试历史项 Schema"""
    id: int
    test_id: int
    test_code: Optional[str] = None
    test_title: Optional[str] = None
    total_score: Optional[int] = None
    result_level: Optional[str] = None
    result_title: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TestHistoryResponseSchema(BaseModel):
    """测试历史响应 Schema"""
    total: int
    items: List[TestHistoryItemSchema]


class TrendDataPointSchema(BaseModel):
    """趋势数据点 Schema"""
    date: str
    score: int


class TestTrendResponseSchema(BaseModel):
    """测试趋势响应 Schema"""
    test_id: int
    test_code: Optional[str] = None
    test_title: Optional[str] = None
    trend_data: List[TrendDataPointSchema]


# ==================== 通用响应 Schemas ====================

class ApiResponse(BaseModel):
    """API 响应基类"""
    code: int = 200
    message: str = "成功"
    data: Optional[Any] = None


# ==================== 综合分析相关 Schemas ====================

class UserInfoSchema(BaseModel):
    """用户信息 Schema"""
    nickname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None


class AnalysisPeriodSchema(BaseModel):
    """分析周期 Schema"""
    days: int
    test_count: int
    earliest_test: str
    latest_test: str


class ComprehensiveAnalysisResponse(BaseModel):
    """综合分析响应 Schema"""
    user_info: UserInfoSchema
    analysis_period: AnalysisPeriodSchema
    test_summary: List[Dict[str, Any]]
    ai_analysis: str
    generated_at: str
