"""通知 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["通知"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """从 token 中获取当前用户 ID"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌")
    return int(user_id)


@router.get("/unread-count", summary="获取未读通知数")
async def get_unread_count(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取当前用户的未读通知数量"""
    try:
        count = NotificationService.get_unread_count(db, user_id)
        return {"code": 200, "message": "获取成功", "data": {"count": count}}
    except Exception as e:
        logger.error(f"获取未读通知数失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", summary="获取通知列表")
async def get_notifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取当前用户的通知列表，含未读总数"""
    try:
        result = NotificationService.get_list(db, user_id, page, page_size)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"获取通知列表失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{notification_id}/read", summary="标记通知已读")
async def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """标记指定通知为已读"""
    try:
        ok = NotificationService.mark_read(db, notification_id, user_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
        return {"code": 200, "message": "已标记为已读"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记已读失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/read-all", summary="全部标记已读")
async def mark_all_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """将当前用户所有未读通知标记为已读"""
    try:
        count = NotificationService.mark_all_read(db, user_id)
        return {"code": 200, "message": "已全部标记为已读", "data": {"updated": count}}
    except Exception as e:
        logger.error(f"全部已读失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
