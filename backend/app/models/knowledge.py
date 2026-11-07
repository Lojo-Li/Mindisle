"""
心理知识相关数据库模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Integer, Boolean, Enum, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class KnowledgeArticle(Base):
    """心理知识文章表"""
    __tablename__ = "knowledge_articles"

    id = Column(BigInteger, primary_key=True, index=True, comment="文章ID")

    # 基本信息
    title = Column(String(200), nullable=False, comment="文章标题")
    summary = Column(String(500), comment="文章摘要")
    cover_image = Column(String(500), comment="封面图片URL")

    # 内容
    content = Column(Text, nullable=False, comment="文章内容（HTML或Markdown）")
    content_type = Column(Enum('markdown', 'html'), default='markdown', comment="内容类型")

    # 分类和标签
    category = Column(String(50), comment="分类（anxiety/depression/emotion/career/family等）")
    tags = Column(String(500), comment="标签（多个用逗号分隔）")

    # 作者信息
    author_id = Column(BigInteger, ForeignKey("users.id"), comment="作者ID")
    author_name = Column(String(100), comment="作者名称")

    # 统计信息
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    favorite_count = Column(Integer, default=0, comment="收藏数")
    comment_count = Column(Integer, default=0, comment="评论数")

    # 状态
    status = Column(Enum('draft', 'published', 'archived'), default='draft', comment="状态")
    is_featured = Column(Boolean, default=False, comment="是否精选")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    # SEO
    seo_keywords = Column(String(200), comment="SEO关键词")
    seo_description = Column(String(500), comment="SEO描述")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    published_at = Column(DateTime, comment="发布时间")

    # 关系
    comments = relationship("KnowledgeComment", back_populates="article")

    def __repr__(self):
        return f"<KnowledgeArticle(id={self.id}, title={self.title})>"


class KnowledgeComment(Base):
    """知识评论表"""
    __tablename__ = "knowledge_comments"

    id = Column(BigInteger, primary_key=True, index=True, comment="评论ID")
    article_id = Column(BigInteger, ForeignKey("knowledge_articles.id"), nullable=False, comment="文章ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")

    # 评论内容
    content = Column(Text, nullable=False, comment="评论内容")
    parent_id = Column(BigInteger, ForeignKey("knowledge_comments.id"), comment="父评论ID（回复功能）")

    # 状态
    is_visible = Column(Boolean, default=True, comment="是否可见")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

    # 点赞
    like_count = Column(Integer, default=0, comment="点赞数")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    article = relationship("KnowledgeArticle", back_populates="comments")
    parent = relationship("KnowledgeComment", remote_side=[id])

    def __repr__(self):
        return f"<KnowledgeComment(id={self.id}, article_id={self.article_id})>"


class KnowledgeFavorite(Base):
    """知识收藏表"""
    __tablename__ = "knowledge_favorites"
    __table_args__ = (
        UniqueConstraint('article_id', 'user_id', name='uq_knowledge_favorites_article_user'),
    )

    id = Column(BigInteger, primary_key=True, index=True, comment="收藏ID")
    article_id = Column(BigInteger, ForeignKey("knowledge_articles.id"), nullable=False, comment="文章ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="收藏时间")

    def __repr__(self):
        return f"<KnowledgeFavorite(article_id={self.article_id}, user_id={self.user_id})>"


class KnowledgeLike(Base):
    """知识点赞表"""
    __tablename__ = "knowledge_likes"
    __table_args__ = (
        UniqueConstraint('article_id', 'user_id', name='uq_knowledge_likes_article_user'),
    )

    id = Column(BigInteger, primary_key=True, index=True, comment="点赞ID")
    article_id = Column(BigInteger, ForeignKey("knowledge_articles.id"), nullable=False, comment="文章ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="点赞时间")

    def __repr__(self):
        return f"<KnowledgeLike(article_id={self.article_id}, user_id={self.user_id})>"


class KnowledgeCommentLike(Base):
    """评论点赞表"""
    __tablename__ = "knowledge_comment_likes"
    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', name='uq_comment_likes_comment_user'),
    )

    id = Column(BigInteger, primary_key=True, index=True, comment="点赞ID")
    comment_id = Column(BigInteger, ForeignKey("knowledge_comments.id"), nullable=False, comment="评论ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")

    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="点赞时间")

    def __repr__(self):
        return f"<KnowledgeCommentLike(comment_id={self.comment_id}, user_id={self.user_id})>"
