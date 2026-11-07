"""
咨询对话 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.counselor import Counselor, ConsultationMessage
from app.schemas.counselor import (
    AppointmentResponse, MessageResponse, MessageListResponse,
    SendMessageRequest, HandleOrderRequest, AddNoteRequest, FileUploadResponse
)
from app.services.counselor_service import ConsultationService

router = APIRouter(prefix="/consultation", tags=["咨询对话"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从 token 中获取当前用户信息"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return int(user_id)


def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """获取当前用户角色"""
    user_id = get_current_user_info(credentials)

    # 检查是否是咨询师
    counselor = db.query(Counselor).filter(
        Counselor.user_id == user_id,
        Counselor.is_deleted == False
    ).first()

    if counselor:
        return 'counselor'
    else:
        return 'user'


# ==================== 咨询师端接口 ====================

@router.get("/counselor/orders", summary="获取咨询师订单列表")
async def get_counselor_orders(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    获取咨询师的预约订单列表

    仅咨询师可访问，支持状态筛选：
    - **pending**: 待确认
    - **confirmed**: 已确认
    - **in_progress**: 进行中
    - **completed**: 已完成
    - **cancelled**: 已取消
    """
    try:
        # 验证是否是咨询师
        counselor = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()
        if not counselor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅咨询师可访问"
            )

        result = ConsultationService.get_counselor_orders(
            db, counselor.id, status_filter, page, page_size
        )
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取咨询师订单列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.post("/order/{order_id}/handle", summary="处理预约订单")
async def handle_order(
    order_id: int,
    handle_data: HandleOrderRequest,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    咨询师处理预约订单

    仅咨询师可访问
    - **action**: agree（同意）/ reject（拒绝）
    - **reason**: 拒绝理由（拒绝时必填）

    处理后会向用户发送系统通知
    """
    try:
        # 验证是否是咨询师
        counselor = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()
        if not counselor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅咨询师可操作"
            )

        ConsultationService.handle_order(
            db, counselor.id, order_id, handle_data.action, handle_data.reason
        )
        return {
            "code": 200,
            "message": "操作成功",
            "data": {
                "order_id": order_id,
                "action": handle_data.action
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"处理订单失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理订单失败: {str(e)}"
        )


# ==================== 对话接口 ====================

@router.get("/{appointment_id}/messages", summary="获取对话消息")
async def get_messages(
    appointment_id: int,
    last_id: Optional[int] = Query(None, description="最后一条消息ID"),
    limit: int = Query(50, ge=1, le=2000, description="获取数量"),
    user_id: int = Depends(get_current_user_info),
    user_type: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    获取咨询对话消息

    支持增量获取（通过last_id参数）
    自动标记对方消息为已读
    """
    try:
        # 如果是咨询师，获取咨询师ID
        actual_user_id = user_id
        if user_type == 'counselor':
            counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id,
                Counselor.is_deleted == False
            ).first()
            if counselor:
                actual_user_id = counselor.id

        result = ConsultationService.get_messages(
            db, appointment_id, actual_user_id, user_type, last_id, limit
        )
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息失败: {str(e)}"
        )


@router.post("/{appointment_id}/message", summary="发送消息")
async def send_message(
    appointment_id: int,
    message_data: SendMessageRequest,
    user_id: int = Depends(get_current_user_info),
    user_type: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    发送咨询对话消息

    支持的消息类型：
    - **text**: 文本消息
    - **image**: 图片消息（需先上传文件）
    - **file**: 文件消息（需先上传文件）

    只能在已确认或进行中的预约中发送消息
    """
    try:
        # 如果是咨询师，获取咨询师ID
        actual_user_id = user_id
        if user_type == 'counselor':
            counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id,
                Counselor.is_deleted == False
            ).first()
            if counselor:
                actual_user_id = counselor.id

        message = ConsultationService.send_message(
            db, appointment_id, actual_user_id, user_type, message_data
        )
        return {
            "code": 200,
            "message": "发送成功",
            "data": message
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_info)
):
    """
    上传咨询文件

    支持的文件类型：
    - 图片：JPG、PNG、GIF
    - 文档：PDF、DOC、DOCX
    - 音频：MP3、WAV

    文件大小限制：10MB
    """
    try:
        # 读取文件数据
        file_data = await file.read()
        filename = file.filename or "file"

        # 上传文件
        file_info = ConsultationService.upload_file(
            file_data=file_data,
            filename=filename,
            content_type=file.content_type
        )

        return {
            "code": 200,
            "message": "上传成功",
            "data": file_info
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.post("/{appointment_id}/end", summary="结束咨询")
async def end_consultation(
    appointment_id: int,
    user_id: int = Depends(get_current_user_info),
    user_type: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    结束咨询会话

    咨询师或用户均可发起
    只能结束状态为"进行中"的咨询
    """
    try:
        # 如果是咨询师，获取咨询师ID
        actual_user_id = user_id
        if user_type == 'counselor':
            counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id,
                Counselor.is_deleted == False
            ).first()
            if counselor:
                actual_user_id = counselor.id

        ConsultationService.end_consultation(
            db, appointment_id, actual_user_id, user_type
        )
        return {
            "code": 200,
            "message": "咨询已结束",
            "data": {
                "appointment_id": appointment_id,
                "ended": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"结束咨询失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结束咨询失败: {str(e)}"
        )


@router.post("/{appointment_id}/note", summary="添加咨询备注")
async def add_consultation_note(
    appointment_id: int,
    note_data: AddNoteRequest,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """
    咨询师添加咨询备注

    仅咨询师可访问
    用于记录咨询过程中的重要信息
    """
    try:
        # 验证是否是咨询师
        counselor = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()
        if not counselor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅咨询师可操作"
            )

        ConsultationService.add_note(
            db, appointment_id, counselor.id, note_data.note
        )
        return {
            "code": 200,
            "message": "备注添加成功",
            "data": {
                "appointment_id": appointment_id,
                "note_added": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"添加备注失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加备注失败: {str(e)}"
        )


@router.delete("/{appointment_id}/signals", summary="清除信令消息")
async def clear_signal_messages(
    appointment_id: int,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    """清除指定预约的所有 WebRTC 信令消息，避免旧信令重复触发"""
    db.query(ConsultationMessage).filter(
        ConsultationMessage.appointment_id == appointment_id,
        ConsultationMessage.message_type.in_(
            ['webrtc_offer', 'webrtc_answer', 'webrtc_ice', 'webrtc_hangup']
        )
    ).delete(synchronize_session=False)
    db.commit()
    return {"code": 200, "message": "清除成功"}
