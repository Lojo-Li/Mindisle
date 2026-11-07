"""
咨询师和预约相关数据库模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Float, Integer, Boolean, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Counselor(Base):
    """咨询师表"""
    __tablename__ = "counselors"

    id = Column(BigInteger, primary_key=True, index=True, comment="咨询师ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), comment="关联用户ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    avatar = Column(String(500), comment="头像URL")
    gender = Column(Enum('male', 'female', 'secret'), default='secret', comment="性别")
    title = Column(String(100), comment="职称")

    # 专业信息
    specialties = Column(String(500), comment="擅长领域（多个用逗号分隔）")
    consultation_types = Column(String(200), comment="咨询方式（video/voice/offline）")
    experience_years = Column(Integer, comment="从业年限")
    education = Column(String(200), comment="学历背景")
    qualifications = Column(String(500), comment="资质证书")

    # 定价信息
    price_video = Column(Float, comment="视频咨询价格（元/小时）")
    price_voice = Column(Float, comment="语音咨询价格（元/小时）")
    price_offline = Column(Float, comment="线下咨询价格（元/小时）")

    # 统计信息
    rating = Column(Float, default=5.0, comment="评分（0-5）")
    review_count = Column(Integer, default=0, comment="评价数量")
    consultation_count = Column(Integer, default=0, comment="咨询次数")

    # 详细信息
    bio = Column(Text, comment="个人简介")
    approach = Column(Text, comment="咨询流派/方法")
    achievements = Column(Text, comment="成就荣誉")

    # 状态
    status = Column(Enum('pending_review', 'active', 'inactive', 'suspended'), default='pending_review', comment="状态")
    is_verified = Column(Boolean, default=False, comment="是否认证")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    # 申请相关字段
    application_status = Column(Enum('pending', 'approved', 'rejected'), default='pending', comment="申请状态")
    rejection_reason = Column(Text, comment="拒绝原因")
    reviewed_at = Column(DateTime, comment="审核时间")
    reviewed_by = Column(BigInteger, comment="审核人ID（管理员）")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime, comment="删除时间")

    # 关系
    appointments = relationship("Appointment", back_populates="counselor")
    reviews = relationship("ConsultationReview", back_populates="counselor")

    def __repr__(self):
        return f"<Counselor(id={self.id}, name={self.name}, status={self.status})>"


class Appointment(Base):
    """预约订单表"""
    __tablename__ = "appointments"

    id = Column(BigInteger, primary_key=True, index=True, comment="预约ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    counselor_id = Column(BigInteger, ForeignKey("counselors.id"), nullable=False, comment="咨询师ID")

    # 预约信息
    appointment_no = Column(String(50), unique=True, index=True, comment="预约编号")
    consultation_type = Column(Enum('video', 'voice', 'offline'), nullable=False, comment="咨询方式")
    appointment_date = Column(DateTime, nullable=False, comment="预约日期时间")
    duration = Column(Integer, default=60, comment="咨询时长（分钟）")

    # 用户信息
    user_name = Column(String(100), comment="预约人姓名")
    user_contact = Column(String(50), comment="联系方式")
    problem_description = Column(Text, comment="问题描述")

    # 价格信息
    price = Column(Float, nullable=False, comment="咨询费用")
    paid_amount = Column(Float, default=0, comment="已付金额")

    # 状态
    status = Column(Enum('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'refunded'),
                   default='pending', comment="订单状态")
    cancel_reason = Column(Text, comment="取消原因")

    # 咨询师备注
    counselor_notes = Column(Text, comment="咨询师备注")

    # 提醒标记
    reminder_sent = Column(Boolean, default=False, comment="是否已发送提醒邮件")
    reminder_sent_at = Column(DateTime, comment="提醒发送时间")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    confirmed_at = Column(DateTime, comment="确认时间")
    completed_at = Column(DateTime, comment="完成时间")
    cancelled_at = Column(DateTime, comment="取消时间")

    # 关系
    counselor = relationship("Counselor", back_populates="appointments")
    review = relationship("ConsultationReview", back_populates="appointment", uselist=False)

    def __repr__(self):
        return f"<Appointment(id={self.id}, no={self.appointment_no}, status={self.status})>"


class ConsultationReview(Base):
    """咨询评价表"""
    __tablename__ = "consultation_reviews"

    id = Column(BigInteger, primary_key=True, index=True, comment="评价ID")
    appointment_id = Column(BigInteger, ForeignKey("appointments.id"), nullable=False, comment="预约ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    counselor_id = Column(BigInteger, ForeignKey("counselors.id"), nullable=False, comment="咨询师ID")

    # 评价内容
    rating = Column(Float, nullable=False, comment="评分（1-5）")
    tags = Column(String(500), comment="评价标签（多个用逗号分隔）")
    content = Column(Text, comment="评价内容")
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")

    # 咨询师回复
    counselor_reply = Column(Text, comment="咨询师回复")
    replied_at = Column(DateTime, comment="回复时间")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    appointment = relationship("Appointment", back_populates="review")
    counselor = relationship("Counselor", back_populates="reviews")

    def __repr__(self):
        return f"<ConsultationReview(id={self.id}, rating={self.rating})>"


class ConsultationMessage(Base):
    """咨询对话消息表"""
    __tablename__ = "consultation_messages"

    id = Column(BigInteger, primary_key=True, index=True, comment="消息ID")
    appointment_id = Column(BigInteger, ForeignKey("appointments.id"), nullable=False, comment="预约ID")
    sender_id = Column(BigInteger, nullable=False, comment="发送者ID")
    sender_type = Column(Enum('user', 'counselor'), nullable=False, comment="发送者类型")

    # 消息内容
    message_type = Column(String(30), default='text', comment="消息类型")
    content = Column(Text, comment="消息内容")
    file_url = Column(String(500), comment="文件URL")
    file_name = Column(String(255), comment="文件名")
    file_size = Column(Integer, comment="文件大小（字节）")

    # 状态
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_at = Column(DateTime, comment="读取时间")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="发送时间")

    def __repr__(self):
        return f"<ConsultationMessage(id={self.id}, type={self.message_type}, sender_type={self.sender_type})>"


class CounselorInquiry(Base):
    """咨询师预约前沟通会话表"""
    __tablename__ = "counselor_inquiries"

    id = Column(BigInteger, primary_key=True, index=True, comment="会话ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    counselor_id = Column(BigInteger, ForeignKey("counselors.id"), nullable=False, comment="咨询师ID")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后消息时间")

    messages = relationship("InquiryMessage", back_populates="inquiry", order_by="InquiryMessage.created_at")

    def __repr__(self):
        return f"<CounselorInquiry(id={self.id}, user={self.user_id}, counselor={self.counselor_id})>"


class InquiryMessage(Base):
    """预约前沟通消息表"""
    __tablename__ = "inquiry_messages"

    id = Column(BigInteger, primary_key=True, index=True, comment="消息ID")
    inquiry_id = Column(BigInteger, ForeignKey("counselor_inquiries.id"), nullable=False, comment="会话ID")
    sender_id = Column(BigInteger, nullable=False, comment="发送者ID")
    sender_role = Column(Enum('user', 'counselor'), nullable=False, comment="发送者角色")
    content = Column(Text, nullable=False, comment="消息内容")
    msg_type = Column(String(20), default='text', comment="消息类型 text/image")

    created_at = Column(DateTime, server_default=func.now(), comment="发送时间")

    inquiry = relationship("CounselorInquiry", back_populates="messages")

    def __repr__(self):
        return f"<InquiryMessage(id={self.id}, role={self.sender_role})>"
