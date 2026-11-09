"""
AI 心理支持 API（E 线）

包含三组接口：
1. 引用溯源：查询某条 AI 回答参考了哪些知识条目
2. 答案反馈：有用 / 没用，用于反哺知识库
3. 风险工单：后台查看与处置风险事件

注意：本路由不改动任何既有接口，只做增量，方便与其他业务线并行开发。
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.chat import ChatDialogue, ChatMessage
from app.schemas.risk import (
    FeedbackCreate, HandleRiskRequest, MessageSourcesResponse,
)
from app.services.risk_service import risk_service

router = APIRouter(prefix="/ai", tags=["AI 心理支持"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """从 token 中解析当前用户 ID"""
    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌"
        )
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证令牌"
        )


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """复用后台认证逻辑，避免重复实现"""
    from app.api.admin import get_current_admin as _admin_dep
    return _admin_dep(credentials=credentials, db=db)


def _assert_message_owner(db: Session, message_id: int, user_id: int) -> ChatMessage:
    """校验这条消息属于当前用户，避免越权读取他人对话"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    dialogue = db.query(ChatDialogue).filter(
        ChatDialogue.id == message.dialogue_id,
        ChatDialogue.user_id == user_id,
    ).first()
    if not dialogue:
        raise HTTPException(status_code=403, detail="无权访问该消息")
    return message


# ==================== 引用溯源 ====================

@router.get("/sources/{message_id}", response_model=dict, summary="查询回答的引用来源")
async def get_message_sources(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    返回某条 AI 回答所引用的知识条目。

    前端在历史会话中重新打开时，用它补回"参考来源"折叠区。
    """
    _assert_message_owner(db, message_id, user_id)
    sources = risk_service.get_message_sources(db, message_id)
    return {
        "code": 200,
        "message": "获取成功",
        "data": MessageSourcesResponse(message_id=message_id, sources=sources).model_dump(),
    }


# ==================== 答案反馈 ====================

@router.post("/feedback", summary="提交答案反馈")
async def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """标记回答是否有用。同一用户重复提交会覆盖旧值。"""
    _assert_message_owner(db, payload.message_id, user_id)
    try:
        risk_service.save_feedback(
            db, user_id, payload.message_id, payload.rating, payload.reason
        )
    except Exception as e:
        db.rollback()
        logger.error(f"保存反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存反馈失败: {e}")
    return {"code": 200, "message": "感谢反馈"}


# ==================== 风险工单（后台） ====================

@router.get("/risk/events", summary="风险工单列表")
async def list_risk_events(
    level: Optional[int] = Query(None, ge=1, le=3, description="风险等级"),
    handled_status: Optional[str] = Query(
        None, pattern=r"^(pending|contacted|closed)$", description="处置状态"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """
    后台风险工单列表。

    按等级与处置状态筛选，默认按时间倒序。
    返回 pending_count 供顶部角标显示待处理数量。
    """
    try:
        data = risk_service.list_events(db, level, handled_status, page, page_size)
        return {"code": 200, "message": "获取成功", "data": data}
    except Exception as e:
        logger.error(f"获取风险工单失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险工单失败: {e}")


@router.put("/risk/events/{event_id}", summary="处置风险事件")
async def handle_risk_event(
    event_id: int,
    payload: HandleRiskRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """标记已联系 / 已关闭，并记录处置备注"""
    try:
        event = risk_service.handle_event(
            db, event_id, payload.handled_status, payload.note, getattr(admin, "id", None)
        )
        return {
            "code": 200,
            "message": "处置成功",
            "data": {
                "id": event.id,
                "level": event.level,
                "handled_status": event.handled_status,
                "note": event.note,
                "handled_at": event.handled_at,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"处置风险事件失败: {e}")
        raise HTTPException(status_code=500, detail=f"处置失败: {e}")


@router.get("/risk/stats", summary="风险事件统计")
async def risk_stats(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """风险总量、待处理数、分级分布、近 7 天趋势"""
    try:
        data = risk_service.stats(db)
        return {"code": 200, "message": "获取成功", "data": data}
    except Exception as e:
        logger.error(f"获取风险统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取风险统计失败: {e}")
