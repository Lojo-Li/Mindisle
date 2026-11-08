"""AI 心理支持相关 Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ========== 引用来源 ==========

class SourceItem(BaseModel):
    """单条引用来源"""
    vector_id: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None
    rank: Optional[int] = None


class MessageSourcesResponse(BaseModel):
    """某条 AI 消息的引用详情"""
    message_id: int
    sources: List[SourceItem] = []


# ========== 风险事件 ==========

class RiskEventResponse(BaseModel):
    """后台风险工单响应"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    dialogue_id: Optional[int] = None
    message_id: Optional[int] = None
    level: int
    level_label: Optional[str] = None
    keywords: Optional[str] = None
    detected_by: Optional[str] = None
    handled_status: str
    handled_by: Optional[int] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    handled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiskEventListResponse(BaseModel):
    total: int
    items: List[RiskEventResponse] = []
    pending_count: int = 0


class HandleRiskRequest(BaseModel):
    """处置风险事件"""
    handled_status: str = Field(..., pattern=r"^(pending|contacted|closed)$")
    note: Optional[str] = Field(None, max_length=500)


# ========== 反馈 ==========

class FeedbackCreate(BaseModel):
    message_id: int
    rating: int = Field(..., ge=-1, le=1, description="1 有用 / -1 没用")
    reason: Optional[str] = Field(None, max_length=200)


# ========== 风险事件统计（后台看板） ==========

class RiskStatsResponse(BaseModel):
    total: int = 0
    pending: int = 0
    by_level: Dict[str, int] = {}
    last_7_days: List[Dict] = []
