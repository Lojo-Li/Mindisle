"""
咨询师预约相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# ==================== 咨询师相关 ====================

class CounselorBase(BaseModel):
    """咨询师基础 Schema"""
    name: str
    gender: Optional[str] = None
    title: Optional[str] = None


class CounselorRegisterRequest(BaseModel):
    """咨询师注册申请请求"""
    # 基本信息
    name: str = Field(..., min_length=2, max_length=100, description="姓名")
    gender: str = Field(..., pattern=r'^(male|female|secret)$', description="性别")
    title: Optional[str] = Field(None, max_length=100, description="职称")

    # 专业信息
    specialties: List[str] = Field(..., min_items=1, description="擅长领域列表")
    consultation_types: List[str] = Field(..., min_items=1, description="咨询方式列表")
    experience_years: int = Field(..., ge=0, le=50, description="从业年限")
    education: str = Field(..., max_length=200, description="学历背景")
    qualifications: str = Field(..., max_length=500, description="资质证书")

    @field_validator('consultation_types')
    @classmethod
    def validate_consultation_types(cls, v):
        """验证咨询方式"""
        valid_types = {'video', 'voice', 'offline'}
        for item in v:
            if item not in valid_types:
                raise ValueError(f'咨询方式必须是: video, voice, offline 之一，实际值: {item}')
        return v

    # 定价信息（元/小时）
    price_video: Optional[float] = Field(None, ge=0, description="视频咨询价格")
    price_voice: Optional[float] = Field(None, ge=0, description="语音咨询价格")
    price_offline: Optional[float] = Field(None, ge=0, description="线下咨询价格")

    # 详细信息
    bio: str = Field(..., min_length=50, max_length=2000, description="个人简介")
    approach: Optional[str] = Field(None, max_length=2000, description="咨询流派/方法")
    achievements: Optional[str] = Field(None, max_length=2000, description="成就荣誉")

    # 证书文件（可选）
    certificate_urls: Optional[List[str]] = Field(None, description="证书文件URL列表")


class CounselorApplicationStatus(BaseModel):
    """咨询师申请状态响应"""
    application_status: str  # pending, approved, rejected
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    can_edit: bool  # 是否可以编辑（仅pending状态可以）


class CounselorResponse(CounselorBase):
    """咨询师响应 Schema"""
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
    rating: float = 5.0
    review_count: int = 0
    consultation_count: int = 0
    bio: Optional[str] = None
    approach: Optional[str] = None
    achievements: Optional[str] = None
    status: str = "active"
    is_verified: bool = False
    application_status: Optional[str] = "pending"
    rejection_reason: Optional[str] = None
    user_email: Optional[str] = Field(None, description="申请人邮箱（审核列表用）")
    has_available_slot: bool = Field(True, description="是否还有可预约时段（用于列表展示可预约/不可预约）")

    model_config = ConfigDict(from_attributes=True)


class CounselorListQuery(BaseModel):
    """咨询师列表查询参数"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    specialties: Optional[List[str]] = Field(None, description="擅长领域列表")
    consultation_types: Optional[List[str]] = Field(None, description="咨询方式列表")
    price_min: Optional[float] = Field(None, description="最低价格")
    price_max: Optional[float] = Field(None, description="最高价格")
    sort: Optional[str] = Field("default", description="排序方式")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


# ==================== 预约相关 ====================

# ==================== 时段发布相关 ====================

class SlotPublishItem(BaseModel):
    """单个待发布时段"""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="时段日期 YYYY-MM-DD")
    start_time: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="开始时间 HH:MM")
    end_time: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="结束时间 HH:MM")


class SlotPublishRequest(BaseModel):
    """批量发布时段请求"""
    slots: List[SlotPublishItem] = Field(..., min_items=1, description="时段列表")


class SlotPublishResult(BaseModel):
    """批量发布结果"""
    created: int = 0
    skipped: int = 0
    conflicts: List[str] = []


class CounselorSlotResponse(BaseModel):
    """咨询师已发布时段响应"""
    id: int
    slot_date: str
    start_time: str
    end_time: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class TimeSlot(BaseModel):
    """可预约时段"""
    time: str  # 时段，如 "09:00-10:00"
    available: bool  # 是否可用
    price: Optional[float] = None  # 该时段价格


class AppointmentCreate(BaseModel):
    """创建预约请求"""
    counselor_id: int = Field(..., description="咨询师ID")
    consultation_type: str = Field(..., pattern=r'^(video|voice|offline)$', description="咨询方式")
    appointment_date: str = Field(..., description="预约日期时间")
    user_name: Optional[str] = Field(None, description="预约人姓名")
    user_contact: Optional[str] = Field(None, description="联系方式")
    problem_description: Optional[str] = Field(None, max_length=1000, description="问题描述")


class AppointmentResponse(BaseModel):
    """预约响应"""
    id: int
    appointment_no: str
    counselor_id: Optional[int] = None
    user_id: int
    consultation_type: str
    appointment_date: datetime
    duration: int
    price: float
    paid_amount: float
    status: str
    user_name: Optional[str] = None
    user_contact: Optional[str] = None
    problem_description: Optional[str] = None
    counselor_notes: Optional[str] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # 关联的咨询师信息
    counselor: Optional['CounselorResponse'] = None

    # 关联的用户信息（用于咨询师查看）
    user_info: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentListResponse(BaseModel):
    """预约列表响应"""
    total: int
    items: List[AppointmentResponse]


# ==================== 评价相关 ====================

class ReviewCreate(BaseModel):
    """创建评价请求"""
    rating: float = Field(..., ge=1, le=5, description="评分")
    tags: Optional[List[str]] = Field(None, description="评价标签")
    content: Optional[str] = Field(None, max_length=500, description="评价内容")
    is_anonymous: bool = Field(False, description="是否匿名")


class ReviewResponse(BaseModel):
    """评价响应"""
    id: int
    appointment_id: int
    rating: float
    tags: Optional[str] = None
    content: Optional[str] = None
    is_anonymous: bool = False
    counselor_reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime

    # 用户信息（如果不匿名）
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    """评价列表响应"""
    total: int
    items: List[ReviewResponse]


# ==================== 统计相关 ====================

class CounselorStats(BaseModel):
    """咨询师统计"""
    total_count: int
    average_rating: float
    total_consultations: int


# ==================== 咨询对话相关 ====================

class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    appointment_id: int
    sender_id: int
    sender_type: str  # user 或 counselor
    message_type: str  # text, image, file, system
    content: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """消息列表响应"""
    total: int
    items: List[MessageResponse]
    has_more: bool = False


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: Optional[str] = Field(None, max_length=20000, description="消息内容")
    message_type: str = Field("text", pattern=r'^(text|image|file|system|webrtc_offer|webrtc_answer|webrtc_ice|webrtc_hangup)$', description="消息类型")
    file_url: Optional[str] = Field(None, description="文件URL")
    file_name: Optional[str] = Field(None, max_length=255, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")


class HandleOrderRequest(BaseModel):
    """处理订单请求"""
    action: str = Field(..., pattern=r'^(agree|reject)$', description="操作：agree同意/reject拒绝")
    reason: Optional[str] = Field(None, max_length=500, description="拒绝理由")


class AddNoteRequest(BaseModel):
    """添加备注请求"""
    note: str = Field(..., max_length=2000, description="备注内容")


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_url: str
    file_name: str
    file_size: int
