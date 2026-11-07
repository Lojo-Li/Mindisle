"""通知模型"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, index=True, comment="通知ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="接收用户ID")
    type = Column(String(50), nullable=False, comment="通知类型")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    related_id = Column(BigInteger, nullable=True, comment="关联业务ID")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
