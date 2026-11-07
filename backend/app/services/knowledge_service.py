"""
心理知识服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.knowledge import KnowledgeArticle, KnowledgeComment, KnowledgeCommentLike, KnowledgeFavorite, KnowledgeLike
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeArticleResponse, KnowledgeListQuery,
    CommentResponse, CommentCreate, CommentListResponse
)


class KnowledgeService:
    """心理知识服务"""

    @staticmethod
    def get_knowledge_list(
        db: Session,
        query: KnowledgeListQuery,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取知识列表"""
        # 构建查询
        q = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.is_deleted == False,
            KnowledgeArticle.status == 'published'
        )

        # 关键词搜索
        if query.keyword:
            q = q.filter(
                or_(
                    KnowledgeArticle.title.contains(query.keyword),
                    KnowledgeArticle.summary.contains(query.keyword),
                    KnowledgeArticle.content.contains(query.keyword),
                    KnowledgeArticle.tags.contains(query.keyword)
                )
            )

        # 分类筛选
        if query.category:
            q = q.filter(KnowledgeArticle.category == query.category)

        # 排序
        if query.sort == "hot":
            q = q.order_by(desc(KnowledgeArticle.view_count))
        elif query.sort == "popular":
            q = q.order_by(desc(KnowledgeArticle.like_count), desc(KnowledgeArticle.favorite_count))
        else:  # latest
            q = q.order_by(desc(KnowledgeArticle.published_at))

        # 总数
        total = q.count()

        # 分页
        offset = (query.page - 1) * query.page_size
        articles = q.offset(offset).limit(query.page_size).all()

        # 转换为响应格式
        items = []
        for article in articles:
            article_data = KnowledgeArticleResponse.model_validate(article)

            # 如果提供了用户ID，查询用户的交互状态
            if user_id:
                is_liked = db.query(KnowledgeLike).filter(
                    KnowledgeLike.article_id == article.id,
                    KnowledgeLike.user_id == user_id
                ).first() is not None

                is_favorited = db.query(KnowledgeFavorite).filter(
                    KnowledgeFavorite.article_id == article.id,
                    KnowledgeFavorite.user_id == user_id
                ).first() is not None

                article_data.is_liked = is_liked
                article_data.is_favorited = is_favorited

            items.append(article_data)

        return {
            "total": total,
            "items": items
        }

    @staticmethod
    def get_knowledge_detail(
        db: Session,
        article_id: int,
        user_id: Optional[int] = None,
        increment_view: bool = True
    ) -> KnowledgeArticleResponse:
        """获取知识详情"""
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()

        if not article:
            raise ValueError("文章不存在")

        # 增加浏览次数
        if increment_view:
            article.view_count += 1
            db.commit()
            db.refresh(article)

        article_data = KnowledgeArticleResponse.model_validate(article)

        # 如果提供了用户ID，查询用户的交互状态
        if user_id:
            is_liked = db.query(KnowledgeLike).filter(
                KnowledgeLike.article_id == article_id,
                KnowledgeLike.user_id == user_id
            ).first() is not None

            is_favorited = db.query(KnowledgeFavorite).filter(
                KnowledgeFavorite.article_id == article_id,
                KnowledgeFavorite.user_id == user_id
            ).first() is not None

            article_data.is_liked = is_liked
            article_data.is_favorited = is_favorited

        return article_data

    @staticmethod
    def get_recommended_knowledge(
        db: Session,
        article_id: int,
        limit: int = 5
    ) -> List[KnowledgeArticleResponse]:
        """获取推荐知识"""
        # 获取当前文章
        current_article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id
        ).first()

        if not current_article:
            raise ValueError("文章不存在")

        # 基于分类和标签推荐
        q = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id != article_id,
            KnowledgeArticle.is_deleted == False,
            KnowledgeArticle.status == 'published'
        )

        # 优先推荐同分类的文章
        if current_article.category:
            q = q.filter(KnowledgeArticle.category == current_article.category)

        # 按浏览量和点赞数排序
        q = q.order_by(desc(KnowledgeArticle.view_count), desc(KnowledgeArticle.like_count))

        articles = q.limit(limit).all()
        return [KnowledgeArticleResponse.model_validate(a) for a in articles]

    @staticmethod
    def toggle_favorite(
        db: Session,
        article_id: int,
        user_id: int,
        action: str
    ) -> bool:
        """收藏/取消收藏"""
        # 验证文章
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()
        if not article:
            raise ValueError("文章不存在")

        if action == "add":
            # 检查是否已收藏
            existing = db.query(KnowledgeFavorite).filter(
                KnowledgeFavorite.article_id == article_id,
                KnowledgeFavorite.user_id == user_id
            ).first()

            if existing:
                return True  # 已收藏

            # 添加收藏
            favorite = KnowledgeFavorite(
                article_id=article_id,
                user_id=user_id
            )
            db.add(favorite)

            try:
                db.flush()
                article.favorite_count += 1
            except IntegrityError:
                db.rollback()
                return True  # 并发下已收藏，视为幂等成功

        elif action == "remove":
            # 删除收藏
            db.query(KnowledgeFavorite).filter(
                KnowledgeFavorite.article_id == article_id,
                KnowledgeFavorite.user_id == user_id
            ).delete()

            # 更新文章收藏数
            if article.favorite_count > 0:
                article.favorite_count -= 1

        db.commit()
        return True

    @staticmethod
    def toggle_like(
        db: Session,
        article_id: int,
        user_id: int,
        action: str
    ) -> bool:
        """点赞/取消点赞"""
        # 验证文章
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()
        if not article:
            raise ValueError("文章不存在")

        if action == "add":
            # 检查是否已点赞
            existing = db.query(KnowledgeLike).filter(
                KnowledgeLike.article_id == article_id,
                KnowledgeLike.user_id == user_id
            ).first()

            if existing:
                return True  # 已点赞

            # 添加点赞
            like = KnowledgeLike(
                article_id=article_id,
                user_id=user_id
            )
            db.add(like)

            try:
                db.flush()
                article.like_count += 1
            except IntegrityError:
                db.rollback()
                return True  # 并发下已点赞，视为幂等成功

        elif action == "remove":
            # 删除点赞
            db.query(KnowledgeLike).filter(
                KnowledgeLike.article_id == article_id,
                KnowledgeLike.user_id == user_id
            ).delete()

            # 更新文章点赞数
            if article.like_count > 0:
                article.like_count -= 1

        db.commit()
        return True

    @staticmethod
    def create_comment(
        db: Session,
        article_id: int,
        user_id: int,
        comment_data: CommentCreate
    ) -> CommentResponse:
        """创建评论"""
        # 验证文章
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()
        if not article:
            raise ValueError("文章不存在")

        # 如果是回复，验证父评论
        if comment_data.parent_id:
            parent_comment = db.query(KnowledgeComment).filter(
                KnowledgeComment.id == comment_data.parent_id,
                KnowledgeComment.article_id == article_id
            ).first()
            if not parent_comment:
                raise ValueError("父评论不存在")

        # 创建评论
        comment = KnowledgeComment(
            article_id=article_id,
            user_id=user_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id
        )

        db.add(comment)

        # 更新文章评论数
        article.comment_count += 1

        db.commit()
        db.refresh(comment)

        comment_data = CommentResponse.model_validate(comment)

        # 添加用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            comment_data.user_name = user.nickname or user.email.split('@')[0]
            comment_data.user_avatar = user.avatar

        return comment_data

    @staticmethod
    def get_comments(
        db: Session,
        article_id: int,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取文章评论列表（含嵌套回复和用户点赞状态）"""
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()
        if not article:
            raise ValueError("文章不存在")

        # 查询顶级评论
        q = db.query(KnowledgeComment).filter(
            KnowledgeComment.article_id == article_id,
            KnowledgeComment.parent_id.is_(None),
            KnowledgeComment.is_visible == True,
            KnowledgeComment.is_deleted == False
        ).order_by(desc(KnowledgeComment.created_at))

        total = q.count()
        offset = (page - 1) * page_size
        comments = q.offset(offset).limit(page_size).all()

        # 收集所有评论的 user_id（用于批量查用户）
        all_user_ids = {c.user_id for c in comments}
        child_comment_ids = []

        # 批量查子回复
        parent_ids = [c.id for c in comments]
        children_map: Dict[int, list] = {}
        if parent_ids:
            child_comments = db.query(KnowledgeComment).filter(
                KnowledgeComment.parent_id.in_(parent_ids),
                KnowledgeComment.is_visible == True,
                KnowledgeComment.is_deleted == False
            ).order_by(KnowledgeComment.created_at).all()

            for child in child_comments:
                children_map.setdefault(child.parent_id, []).append(child)
                all_user_ids.add(child.user_id)
                child_comment_ids.append(child.id)

        # 批量查用户信息
        users_map = {}
        if all_user_ids:
            users = db.query(User).filter(User.id.in_(all_user_ids)).all()
            users_map = {u.id: u for u in users}

        # 批量查评论点赞状态
        all_comment_ids = [c.id for c in comments] + child_comment_ids
        liked_comment_ids = set()
        if user_id and all_comment_ids:
            likes = db.query(KnowledgeCommentLike).filter(
                KnowledgeCommentLike.comment_id.in_(all_comment_ids),
                KnowledgeCommentLike.user_id == user_id
            ).all()
            liked_comment_ids = {l.comment_id for l in likes}

        # 组装响应
        items = []
        for comment in comments:
            comment_data = _build_comment_response(comment, users_map, liked_comment_ids)
            children = children_map.get(comment.id, [])
            comment_data.reply_count = len(children)
            comment_data.children = [
                _build_comment_response(child, users_map, liked_comment_ids)
                for child in children[:10]
            ]
            items.append(comment_data)

        return {
            "total": total,
            "items": items
        }

    @staticmethod
    def toggle_comment_like(
        db: Session,
        comment_id: int,
        user_id: int,
        action: str
    ) -> Dict[str, Any]:
        """点赞/取消点赞评论"""
        comment = db.query(KnowledgeComment).filter(
            KnowledgeComment.id == comment_id,
            KnowledgeComment.is_deleted == False
        ).first()
        if not comment:
            raise ValueError("评论不存在")

        if action == "add":
            existing = db.query(KnowledgeCommentLike).filter(
                KnowledgeCommentLike.comment_id == comment_id,
                KnowledgeCommentLike.user_id == user_id
            ).first()
            if existing:
                return {"liked": True, "like_count": comment.like_count}

            like = KnowledgeCommentLike(comment_id=comment_id, user_id=user_id)
            db.add(like)
            try:
                db.flush()
                comment.like_count += 1
            except IntegrityError:
                db.rollback()
                return {"liked": True, "like_count": comment.like_count}

        elif action == "remove":
            deleted = db.query(KnowledgeCommentLike).filter(
                KnowledgeCommentLike.comment_id == comment_id,
                KnowledgeCommentLike.user_id == user_id
            ).delete()
            if deleted and comment.like_count > 0:
                comment.like_count -= 1

        db.commit()
        return {"liked": action == "add", "like_count": comment.like_count}

    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: int,
        user_id: int
    ) -> int:
        """删除评论（软删除 + 级联子回复 + 同步文章评论计数）"""
        comment = db.query(KnowledgeComment).filter(
            KnowledgeComment.id == comment_id,
            KnowledgeComment.is_deleted == False
        ).first()
        if not comment:
            raise ValueError("评论不存在")
        if comment.user_id != user_id:
            raise ValueError("无权删除此评论")

        # 统计本次要软删除的数量（自身 + 所有子回复）
        to_delete_count = 1
        child_ids = [comment.id]
        while child_ids:
            children = db.query(KnowledgeComment).filter(
                KnowledgeComment.parent_id.in_(child_ids),
                KnowledgeComment.is_deleted == False
            ).all()
            for c in children:
                c.is_deleted = True
                to_delete_count += 1
            child_ids = [c.id for c in children]

        comment.is_deleted = True

        # 同步文章评论计数
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == comment.article_id
        ).first()
        if article and article.comment_count >= to_delete_count:
            article.comment_count -= to_delete_count
        elif article:
            article.comment_count = 0

        db.commit()
        return to_delete_count

    @staticmethod
    def get_user_favorites(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取用户收藏列表"""
        # 查询收藏
        q = db.query(KnowledgeArticle).join(
            KnowledgeFavorite,
            KnowledgeArticle.id == KnowledgeFavorite.article_id
        ).filter(
            KnowledgeFavorite.user_id == user_id,
            KnowledgeArticle.is_deleted == False
        ).order_by(desc(KnowledgeFavorite.created_at))

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        articles = q.offset(offset).limit(page_size).all()

        items = []
        for article in articles:
            article_data = KnowledgeArticleResponse.model_validate(article)
            article_data.is_favorited = True  # 收藏列表中的文章肯定是已收藏的
            items.append(article_data)

        return {
            "total": total,
            "items": items
        }


def _build_comment_response(
    comment: KnowledgeComment,
    users_map: dict,
    liked_comment_ids: set
) -> CommentResponse:
    """构建单条评论的响应对象"""
    comment_data = CommentResponse.model_validate(comment)
    user = users_map.get(comment.user_id)
    if user:
        comment_data.user_name = user.nickname or (user.email.split('@')[0] if user.email else '用户')
        comment_data.user_avatar = user.avatar
    comment_data.is_liked = comment.id in liked_comment_ids
    return comment_data
