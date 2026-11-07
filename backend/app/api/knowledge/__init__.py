"""
心理知识 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.knowledge import (
    KnowledgeArticleResponse, KnowledgeListQuery,
    CommentResponse, CommentCreate
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["心理知识"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[int]:
    """从 token 中获取当前用户 ID（可选认证）"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            return int(payload.get("sub"))
        return None
    except:
        return None


# ==================== 知识文章接口 ====================

@router.get("/list", summary="获取知识列表")
async def get_knowledge_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    sort: Optional[str] = Query("latest", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    获取心理知识列表

    支持多维度筛选：
    - **keyword**: 搜索标题、摘要、内容、标签
    - **category**: 分类筛选（anxiety/depression/emotion/career/family等）
    - **sort**: 排序方式（latest最新/hot热门/popular推荐）

    返回分页列表数据，包含用户的点赞和收藏状态
    """
    try:
        query = KnowledgeListQuery(
            keyword=keyword,
            category=category,
            sort=sort,
            page=page,
            page_size=page_size
        )
        result = KnowledgeService.get_knowledge_list(db, query, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取知识列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识列表失败: {str(e)}"
        )


@router.get("/{article_id}", summary="获取知识详情")
async def get_knowledge_detail(
    article_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    获取知识文章详情

    返回文章完整内容，包括：
    - 基本信息（标题、摘要、封面）
    - 文章内容（Markdown/HTML）
    - 分类和标签
    - 统计信息（浏览、点赞、收藏、评论）
    - 用户交互状态（是否已点赞、收藏）
    """
    try:
        article = KnowledgeService.get_knowledge_detail(db, article_id, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": article
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取知识详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识详情失败: {str(e)}"
        )


@router.get("/{article_id}/recommended", summary="获取推荐知识")
async def get_recommended_knowledge(
    article_id: int,
    limit: int = Query(5, ge=1, le=10, description="推荐数量"),
    db: Session = Depends(get_db)
):
    """
    获取推荐知识文章

    基于当前文章的分类和标签推荐相关内容
    优先推荐同分类的热门文章
    """
    try:
        articles = KnowledgeService.get_recommended_knowledge(db, article_id, limit)
        return {
            "code": 200,
            "message": "获取成功",
            "data": articles
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取推荐知识失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐知识失败: {str(e)}"
        )


# ==================== 交互功能接口 ====================

@router.post("/{article_id}/favorite", summary="收藏知识")
async def favorite_knowledge(
    article_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    收藏知识文章

    如果已收藏则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_favorite(db, article_id, user_id, "add")
        return {
            "code": 200,
            "message": "收藏成功",
            "data": {
                "article_id": article_id,
                "favorited": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"收藏失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏失败: {str(e)}"
        )


@router.delete("/{article_id}/favorite", summary="取消收藏知识")
async def unfavorite_knowledge(
    article_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消收藏知识文章

    如果未收藏则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_favorite(db, article_id, user_id, "remove")
        return {
            "code": 200,
            "message": "已取消收藏",
            "data": {
                "article_id": article_id,
                "favorited": False
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消收藏失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消收藏失败: {str(e)}"
        )


@router.post("/{article_id}/like", summary="点赞知识")
async def like_knowledge(
    article_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    点赞知识文章

    如果已点赞则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_like(db, article_id, user_id, "add")
        return {
            "code": 200,
            "message": "点赞成功",
            "data": {
                "article_id": article_id,
                "liked": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞失败: {str(e)}"
        )


@router.delete("/{article_id}/like", summary="取消点赞知识")
async def unlike_knowledge(
    article_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消点赞知识文章

    如果未点赞则忽略，支持重复调用
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        KnowledgeService.toggle_like(db, article_id, user_id, "remove")
        return {
            "code": 200,
            "message": "已取消点赞",
            "data": {
                "article_id": article_id,
                "liked": False
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消点赞失败: {str(e)}"
        )


# ==================== 评论接口 ====================

@router.get("/{article_id}/comments", summary="获取文章评论")
async def get_comments(
    article_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id)
):
    """
    获取文章评论列表

    返回顶级评论及一级子回复（最多2层嵌套）
    按创建时间倒序排列
    未登录用户亦可查看，但不含点赞状态
    """
    try:
        result = KnowledgeService.get_comments(db, article_id, page, page_size, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取评论失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论失败: {str(e)}"
        )


@router.post("/{article_id}/comment", summary="提交评论")
async def create_comment(
    article_id: int,
    comment_data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交文章评论

    支持两种评论类型：
    - 直接评论（不提供parent_id）
    - 回复评论（提供parent_id）

    评论内容1-1000字符
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        comment = KnowledgeService.create_comment(db, article_id, user_id, comment_data)
        return {
            "code": 200,
            "message": "评论成功",
            "data": comment
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"提交评论失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交评论失败: {str(e)}"
        )


# ==================== 评论互动接口 ====================

@router.post("/comments/{comment_id}/like", summary="点赞评论")
async def like_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """点赞评论"""
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )
        result = KnowledgeService.toggle_comment_like(db, comment_id, user_id, "add")
        return {
            "code": 200,
            "message": "点赞成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"评论点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论点赞失败: {str(e)}"
        )


@router.delete("/comments/{comment_id}/like", summary="取消点赞评论")
async def unlike_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """取消点赞评论"""
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )
        result = KnowledgeService.toggle_comment_like(db, comment_id, user_id, "remove")
        return {
            "code": 200,
            "message": "已取消点赞",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消评论点赞失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消评论点赞失败: {str(e)}"
        )


@router.delete("/comments/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除评论（仅评论作者可删除，会级联删除所有子回复）"""
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )
        deleted_count = KnowledgeService.delete_comment(db, comment_id, user_id)
        return {
            "code": 200,
            "message": f"已删除 {deleted_count} 条评论",
            "data": {"deleted_count": deleted_count}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除评论失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除评论失败: {str(e)}"
        )


# ==================== 用户收藏接口 ====================

@router.get("/user/favorites", summary="获取用户收藏列表")
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的收藏列表

    按收藏时间倒序排列
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        result = KnowledgeService.get_user_favorites(db, user_id, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取收藏列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏列表失败: {str(e)}"
        )
