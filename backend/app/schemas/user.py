"""
用户相关的 Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    """用户基础 Schema"""
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    """用户创建 Schema"""
    password: str = Field(..., min_length=6, max_length=20)


class UserLogin(BaseModel):
    """用户登录 Schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """用户更新 Schema"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    role: str
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 响应 Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据 Schema"""
    user_id: Optional[int] = None
    email: Optional[str] = None


# ==================== 个人中心相关 Schemas ====================

class UserProfileResponse(BaseModel):
    """用户资料响应"""
    id: int
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    role: str = "user"
    status: str = "active"
    is_verified: bool = False
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """用户资料更新请求"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=20, description="昵称")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    birth_date: Optional[date] = Field(None, description="出生日期")
    gender: Optional[str] = Field(None, pattern=r'^(male|female|secret)$', description="性别")
    bio: Optional[str] = Field(None, max_length=200, description="个人简介")


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    avatar: str


class PrivacySettings(BaseModel):
    """隐私设置"""
    save_chat_history: bool = True
    chat_visible: bool = True          # True=允许管理员查看, False=仅自己可见
    save_test_records: bool = True
    allow_trend_analysis: bool = True
    # deprecated fields kept for backward compatibility
    allow_ai_analysis: bool = False
    chat_only_visible: bool = False
    test_only_visible: bool = False


class UserStatistics(BaseModel):
    """用户统计数据"""
    test_count: int = 0
    chat_count: int = 0
    appointment_count: int = 0
    favorite_count: int = 0


class ActivityTrendItem(BaseModel):
    """活动趋势项"""
    date: str
    count: int


class TestDistributionItem(BaseModel):
    """测试分布项"""
    name: str
    value: int


class ChatDistributionItem(BaseModel):
    """对话分布项"""
    name: str
    count: int


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
