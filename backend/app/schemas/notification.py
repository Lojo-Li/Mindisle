"""通知相关的 Pydantic Schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    user_id: int
    type: str
    title: str
    content: str
    related_id: Optional[int] = None
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    total: int
    items: list[NotificationResponse]
    unread_count: int
    page: int
    page_size: int
