"""
聊天相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 标签相关 Schemas ==========
class TagBase(BaseModel):
    """标签基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#1890ff"


class TagCreate(TagBase):
    """标签创建 Schema"""
    pass


class TagResponse(TagBase):
    """标签响应 Schema"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 消息相关 Schemas ==========
class MessageBase(BaseModel):
    """消息基础 Schema"""
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """消息创建 Schema"""
    type: str = "text"  # 消息类型：text/voice


class MessageResponse(MessageBase):
    """消息响应 Schema"""
    id: int
    dialogue_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 对话相关 Schemas ==========
class DialogueBase(BaseModel):
    """对话基础 Schema"""
    title: str = "新对话"


class DialogueCreate(DialogueBase):
    """对话创建 Schema"""
    tag_ids: Optional[List[int]] = []  # 关联的标签ID列表


class DialogueUpdate(BaseModel):
    """对话更新 Schema"""
    title: str


class DialogueResponse(DialogueBase):
    """对话响应 Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    message_count: int = 0  # 消息数量
    tags: List[TagResponse] = []  # 关联的标签

    class Config:
        from_attributes = True


class DialogueListResponse(BaseModel):
    """对话列表响应 Schema"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    tags: List[TagResponse] = []
    last_message: Optional[str] = None  # 最后一条消息预览

    class Config:
        from_attributes = True


class DialogueDetailResponse(BaseModel):
    """对话详情响应 Schema"""
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]
    tags: List[TagResponse]

    class Config:
        from_attributes = True


# ========== 聊天请求/响应 Schemas ==========
class ChatRequest(BaseModel):
    """聊天请求 Schema"""
    message: str = Field(..., min_length=1)
    stream: bool = False  # 是否流式返回


class ChatResponse(BaseModel):
    """聊天响应 Schema"""
    message_id: int
    reply: str
    created_at: datetime


# ========== 语音转文字 Schema ==========
class VoiceToTextRequest(BaseModel):
    """语音转文字请求 Schema"""
    audio_url: str


class VoiceToTextResponse(BaseModel):
    """语音转文字响应 Schema"""
    text: str
