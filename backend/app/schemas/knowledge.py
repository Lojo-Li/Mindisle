"""
心理知识相关的 Pydantic Schemas
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== 知识文章相关 ====================

class KnowledgeArticleResponse(BaseModel):
    """知识文章响应"""
    id: int
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    content: str
    content_type: str = "markdown"
    category: Optional[str] = None
    tags: Optional[str] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    favorite_count: int = 0
    comment_count: int = 0
    status: str = "draft"
    is_featured: bool = False
    seo_keywords: Optional[str] = None
    seo_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    # 用户交互状态（可选）
    is_liked: Optional[bool] = False
    is_favorited: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class KnowledgeListQuery(BaseModel):
    """知识列表查询参数"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="分类筛选")
    sort: Optional[str] = Field("latest", description="排序方式（latest/popular/hot）")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class KnowledgeListResponse(BaseModel):
    """知识列表响应"""
    total: int
    items: List[KnowledgeArticleResponse]


# ==================== 评论相关 ====================

class CommentResponse(BaseModel):
    """评论响应"""
    id: int
    article_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    like_count: int = 0
    created_at: datetime

    # 用户信息
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    # 交互状态
    is_liked: Optional[bool] = False

    # 子回复
    reply_count: int = 0
    children: Optional[List['CommentResponse']] = None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID（回复时使用）")


class CommentListResponse(BaseModel):
    """评论列表响应"""
    total: int
    items: List[CommentResponse]


CommentResponse.model_rebuild()
