"""
聊天模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatDialogue(Base):
    """对话表"""
    __tablename__ = "chat_dialogues"

    id = Column(BigInteger, primary_key=True, index=True, comment="对话ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(255), default="新对话", comment="对话标题")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    messages = relationship("ChatMessage", back_populates="dialogue", cascade="all, delete-orphan")
    tags = relationship("ChatDialogueTag", back_populates="dialogue", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatDialogue(id={self.id}, title={self.title}, user_id={self.user_id})>"


class ChatMessage(Base):
    """消息表"""
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, index=True, comment="消息ID")
    dialogue_id = Column(BigInteger, ForeignKey("chat_dialogues.id"), nullable=False, comment="对话ID")
    role = Column(String(20), nullable=False, comment="角色：user/assistant")
    content = Column(Text, nullable=False, comment="消息内容")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    dialogue = relationship("ChatDialogue", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, dialogue_id={self.dialogue_id})>"


class ChatTag(Base):
    """标签表"""
    __tablename__ = "chat_tags"

    id = Column(BigInteger, primary_key=True, index=True, comment="标签ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(50), nullable=False, comment="标签名称")
    color = Column(String(20), default="#1890ff", comment="标签颜色")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    dialogue_tags = relationship("ChatDialogueTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatTag(id={self.id}, name={self.name}, user_id={self.user_id})>"


class ChatDialogueTag(Base):
    """对话标签关联表"""
    __tablename__ = "chat_dialogue_tags"

    id = Column(BigInteger, primary_key=True, index=True, comment="关联ID")
    dialogue_id = Column(BigInteger, ForeignKey("chat_dialogues.id"), nullable=False, comment="对话ID")
    tag_id = Column(BigInteger, ForeignKey("chat_tags.id"), nullable=False, comment="标签ID")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    dialogue = relationship("ChatDialogue", back_populates="tags")
    tag = relationship("ChatTag", back_populates="dialogue_tags")

    def __repr__(self):
        return f"<ChatDialogueTag(dialogue_id={self.dialogue_id}, tag_id={self.tag_id})>"
