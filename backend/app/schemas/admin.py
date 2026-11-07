"""
后台管理相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== 管理员相关 ====================

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class AdminResponse(BaseModel):
    """管理员响应"""
    id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminTokenResponse(BaseModel):
    """管理员Token响应"""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse


# ==================== 仪表盘相关 ====================

class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    user_count: int = 0
    counselor_count: int = 0
    order_count: int = 0
    article_count: int = 0
    today_user_count: int = 0
    today_order_count: int = 0
    total_revenue: float = 0
    pending_counselor_count: int = 0


class ChartDataPoint(BaseModel):
    """图表数据点"""
    date: str
    value: float
    label: Optional[str] = None


class ChartResponse(BaseModel):
    """图表数据响应"""
    type: str
    data: List[ChartDataPoint]
    total: Optional[float] = None


# ==================== 咨询师审核相关 ====================

class CounselorReviewResponse(BaseModel):
    """咨询师审核响应"""
    id: int
    name: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    title: Optional[str] = None
    specialties: Optional[str] = None
    consultation_types: Optional[str] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    qualifications: Optional[str] = None
    price_video: Optional[float] = None
    price_voice: Optional[float] = None
    price_offline: Optional[float] = None
    bio: Optional[str] = None
    approach: Optional[str] = None
    achievements: Optional[str] = None
    application_status: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewCounselorRequest(BaseModel):
    """审核咨询师请求"""
    action: str = Field(..., pattern=r'^(approve|reject)$', description="操作：approve同意/reject拒绝")
    reason: Optional[str] = Field(None, max_length=500, description="拒绝理由")


# ==================== 知识管理相关 ====================

class ArticleSaveRequest(BaseModel):
    """保存文章请求"""
    id: Optional[int] = Field(None, description="文章ID（更新时提供）")
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    summary: Optional[str] = Field(None, max_length=500, description="摘要")
    cover_image: Optional[str] = Field(None, description="封面图URL")
    content: str = Field(..., description="内容（HTML或Markdown）")
    content_type: str = Field("markdown", pattern=r'^(markdown|html)$', description="内容类型")
    category: Optional[str] = Field(None, description="分类")
    tags: Optional[str] = Field(None, description="标签（逗号分隔）")
    status: str = Field("draft", pattern=r'^(draft|published|archived)$', description="状态")
    seo_keywords: Optional[str] = Field(None, description="SEO关键词")
    seo_description: Optional[str] = Field(None, description="SEO描述")


# ==================== 用户管理相关 ====================

class AdminUserResponse(BaseModel):
    """后台用户响应（返回给前端的格式）"""
    id: int
    email: str
    username: Optional[str] = None    # 用 email 填充
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"
    gender: Optional[str] = None
    birthDate: Optional[str] = None   # birth_date 格式化后
    bio: Optional[str] = None
    banned: bool = False              # status == 'banned'
    status: str = "active"
    is_verified: bool = False
    lastLoginTime: Optional[str] = None  # last_login_at 格式化后
    createdAt: Optional[str] = None      # created_at 格式化后

    # 统计信息（camelCase，与前端一致）
    testCount: int = 0
    chatCount: int = 0
    appointmentCount: int = 0
    favoriteCount: int = 0

    model_config = ConfigDict(from_attributes=False)


class BanUserRequest(BaseModel):
    """封禁用户请求"""
    banned: bool = Field(..., description="是否封禁")
    reason: Optional[str] = Field(None, max_length=500, description="封禁理由")


# ==================== 订单管理相关 ====================

class AdminOrderResponse(BaseModel):
    """后台订单响应"""
    id: int
    appointment_no: str
    user_id: int
    user_name: Optional[str] = None
    user_contact: Optional[str] = None
    counselor_id: int
    counselor_name: Optional[str] = None
    consultation_type: str
    appointment_date: datetime
    price: float
    paid_amount: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
