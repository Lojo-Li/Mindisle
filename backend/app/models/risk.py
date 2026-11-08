"""
AI 心理支持相关数据模型（E 线）

三张表分别解决三个问题：
- RiskEvent      : 风险信号有没有人接住（可追溯、可统计、可处置）
- AiMessageSource: AI 这句话的依据是什么（引用溯源）
- AiFeedback     : 回答好不好用（反哺知识库）

注意：这里不声明 ForeignKey。
原因：init.sql 里主键是 BIGINT UNSIGNED，而 SQLAlchemy 的 BigInteger 是有符号的，
两者混用时 Base.metadata.create_all 会因为外键类型不兼容直接报错。
外键约束统一由 sql/migrate_e_ai_support.sql 维护，ORM 只保证索引与查询。
"""
from sqlalchemy import (
    Column, BigInteger, String, Text, SmallInteger, Float,
    DateTime, Enum, func, Index, UniqueConstraint
)
from app.core.database import Base


class RiskEvent(Base):
    """风险事件表"""
    __tablename__ = "risk_events"

    id = Column(BigInteger, primary_key=True, index=True, comment="事件ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID（外键见 DDL）")
    dialogue_id = Column(BigInteger, comment="对话ID（外键见 DDL）")
    message_id = Column(BigInteger, comment="触发消息ID（外键见 DDL）")

    level = Column(SmallInteger, nullable=False, comment="风险等级：1关注 2警示 3紧急")
    keywords = Column(String(300), comment="命中的关键词，逗号分隔")
    detected_by = Column(
        Enum("keyword", "model", "manual"), default="keyword", comment="识别来源"
    )
    action_taken = Column(String(200), comment="已执行的处置动作")

    handled_status = Column(
        Enum("pending", "contacted", "closed"), default="pending", comment="处置状态"
    )
    handled_by = Column(BigInteger, comment="处置人（外键见 DDL）")
    note = Column(String(500), comment="处置备注")
    handled_at = Column(DateTime, comment="处置时间")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index("idx_risk_level_status", "level", "handled_status"),
        Index("idx_risk_user", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<RiskEvent(id={self.id}, user_id={self.user_id}, level={self.level})>"


class AiMessageSource(Base):
    """AI 回答的引用来源表"""
    __tablename__ = "ai_message_sources"

    id = Column(BigInteger, primary_key=True, index=True, comment="主键")
    message_id = Column(
        BigInteger, nullable=False, comment="AI 消息ID（外键见 DDL）"
    )
    vector_id = Column(String(64), comment="ChromaDB 中的向量ID")
    doc_title = Column(String(200), comment="知识条目标题")
    snippet = Column(Text, comment="引用片段")
    score = Column(Float, comment="相似度 0~1")
    rank = Column(SmallInteger, comment="排序，1 为最相关")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index("idx_source_message", "message_id"),
    )

    def __repr__(self):
        return f"<AiMessageSource(message_id={self.message_id}, rank={self.rank})>"


class AiFeedback(Base):
    """AI 回答反馈表"""
    __tablename__ = "ai_feedback"

    id = Column(BigInteger, primary_key=True, index=True, comment="主键")
    message_id = Column(
        BigInteger, nullable=False, comment="AI 消息ID（外键见 DDL）"
    )
    user_id = Column(BigInteger, nullable=False, comment="用户ID（外键见 DDL）")
    rating = Column(SmallInteger, comment="1 有用 / -1 没用")
    reason = Column(String(200), comment="原因")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_feedback_message_user"),
    )

    def __repr__(self):
        return f"<AiFeedback(message_id={self.message_id}, rating={self.rating})>"
