"""
咨询师预约 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.counselor import (
    CounselorResponse, CounselorListQuery, CounselorRegisterRequest,
    TimeSlot, AppointmentCreate, AppointmentResponse,
    ReviewCreate, ReviewResponse
)
from app.services.counselor_service import CounselorService, AppointmentService

router = APIRouter(prefix="/counselor", tags=["咨询师预约"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """从 token 中获取当前用户 ID"""
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


# ==================== 咨询师接口 ====================

@router.get("/list", summary="获取咨询师列表")
async def get_counselor_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    specialties: Optional[str] = Query(None, description="擅长领域(多个用逗号分隔)"),
    consultation_types: Optional[str] = Query(None, description="咨询方式(多个用逗号分隔)"),
    price_min: Optional[float] = Query(None, description="最低价格"),
    price_max: Optional[float] = Query(None, description="最高价格"),
    sort: Optional[str] = Query("default", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取咨询师列表

    支持多维度筛选：
    - **keyword**: 搜索咨询师姓名、擅长领域
    - **specialties**: 擅长领域（多个用逗号分隔，如：anxiety,depression）
    - **consultation_types**: 咨询方式（多个用逗号分隔，如：video,voice）
    - **price_min/price_max**: 价格范围
    - **sort**: 排序方式（default/rating/orders/price-asc）

    返回分页列表数据
    """
    try:
        # 处理多选参数
        specialty_list = specialties.split(',') if specialties else None
        consultation_type_list = consultation_types.split(',') if consultation_types else None

        query = CounselorListQuery(
            keyword=keyword,
            specialties=specialty_list,
            consultation_types=consultation_type_list,
            price_min=price_min,
            price_max=price_max,
            sort=sort,
            page=page,
            page_size=page_size
        )
        result = CounselorService.get_counselor_list(db, query)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取咨询师列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取咨询师列表失败: {str(e)}"
        )


@router.get("/{counselor_id}", summary="获取咨询师详情")
async def get_counselor_detail(
    counselor_id: int,
    db: Session = Depends(get_db)
):
    """
    获取咨询师详细信息

    返回咨询师完整资料，包括：
    - 基本信息（姓名、职称、性别等）
    - 专业信息（擅长领域、从业年限、学历等）
    - 定价信息（各咨询方式价格）
    - 统计信息（评分、评价数、咨询次数）
    - 详细介绍（简介、咨询方法、成就等）
    """
    try:
        counselor = CounselorService.get_counselor_detail(db, counselor_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": counselor
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取咨询师详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取咨询师详情失败: {str(e)}"
        )


@router.get("/{counselor_id}/slots", summary="获取可预约时段")
async def get_available_slots(
    counselor_id: int,
    date: str = Query(..., description="预约日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    获取咨询师指定日期的可预约时段

    返回所有时段（09:00-18:00）的可用状态：
    - **time**: 时段
    - **available**: 是否可用
    - **price**: 该时段价格

    已被预约的时段会标记为不可用
    """
    try:
        slots = CounselorService.get_available_slots(db, counselor_id, date)
        return {
            "code": 200,
            "message": "获取成功",
            "data": slots
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取可预约时段失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可预约时段失败: {str(e)}"
        )


@router.get("/{counselor_id}/reviews", summary="获取咨询师评价列表")
async def get_counselor_reviews(
    counselor_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取咨询师的评价列表

    返回分页的评价数据，包括：
    - 评分和评价内容
    - 评价标签
    - 咨询师回复
    - 用户信息（匿名评价不显示）
    """
    try:
        result = CounselorService.get_counselor_reviews(db, counselor_id, page, page_size)
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
        logger.error(f"获取评价列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价列表失败: {str(e)}"
        )


from app.models.counselor import CounselorInquiry, InquiryMessage


# ==================== 预约前沟通接口 ====================

router_inquiry = APIRouter(prefix="/inquiry", tags=["预约前沟通"])


@router_inquiry.post("/{counselor_id}/start", summary="开启/获取与咨询师的沟通会话")
async def start_inquiry(
    counselor_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取已有会话，若不存在则创建新会话，返回 inquiry_id"""
    counselor = db.query(__import__('app.models.counselor', fromlist=['Counselor']).Counselor).filter_by(
        id=counselor_id, is_deleted=False
    ).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    inquiry = db.query(CounselorInquiry).filter_by(
        user_id=user_id, counselor_id=counselor_id
    ).first()
    if not inquiry:
        inquiry = CounselorInquiry(user_id=user_id, counselor_id=counselor_id)
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "inquiry_id": inquiry.id,
            "counselor_id": counselor_id,
            "counselor_name": counselor.name,
            "counselor_avatar": counselor.avatar,
            "counselor_title": counselor.title,
        }
    }


@router_inquiry.get("/{inquiry_id}/messages", summary="获取会话消息列表")
async def get_inquiry_messages(
    inquiry_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    inquiry = db.query(CounselorInquiry).filter_by(id=inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="会话不存在")
    if inquiry.user_id != user_id:
        # 咨询师侧也可访问（此时 user_id 对应咨询师账号，暂简化鉴权）
        from app.models.counselor import Counselor as CounselorModel
        counselor = db.query(CounselorModel).filter_by(user_id=user_id, id=inquiry.counselor_id).first()
        if not counselor:
            raise HTTPException(status_code=403, detail="无权访问此会话")

    msgs = db.query(InquiryMessage).filter_by(inquiry_id=inquiry_id).order_by(InquiryMessage.created_at).all()
    return {
        "code": 200,
        "message": "ok",
        "data": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "sender_role": m.sender_role,
                "content": m.content,
                "msg_type": m.msg_type,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in msgs
        ]
    }


@router_inquiry.post("/{inquiry_id}/message", summary="发送消息")
async def send_inquiry_message(
    inquiry_id: int,
    body: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    inquiry = db.query(CounselorInquiry).filter_by(id=inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 判断发送者角色
    from app.models.counselor import Counselor as CounselorModel
    counselor = db.query(CounselorModel).filter_by(user_id=user_id, id=inquiry.counselor_id).first()
    role = "counselor" if counselor else "user"

    msg = InquiryMessage(
        inquiry_id=inquiry_id,
        sender_id=user_id,
        sender_role=role,
        content=body.get("content", ""),
        msg_type=body.get("msg_type", "text"),
    )
    db.add(msg)
    # 更新会话时间
    from datetime import datetime
    inquiry.updated_at = datetime.now()
    db.commit()
    db.refresh(msg)

    return {
        "code": 200,
        "message": "发送成功",
        "data": {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_role": msg.sender_role,
            "content": msg.content,
            "msg_type": msg.msg_type,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
    }


# ==================== 预约接口 ====================

router_appointment = APIRouter(prefix="/appointment", tags=["预约管理"])


@router_appointment.post("/create", summary="创建预约订单")
async def create_appointment(
    appointment_data: AppointmentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建新的预约订单

    创建预约前会验证：
    - 咨询师存在且状态正常
    - 预约时间有效（不能是过去）
    - 该时段未被预约
    - 咨询师支持所选咨询方式

    成功创建后返回订单详情
    """
    try:
        appointment = AppointmentService.create_appointment(db, user_id, appointment_data)
        return {
            "code": 200,
            "message": "预约创建成功",
            "data": appointment
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建预约失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建预约失败: {str(e)}"
        )


@router_appointment.get("/user/list", summary="获取用户预约列表")
async def get_user_appointments(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的预约列表

    支持状态筛选：
    - **pending**: 待确认
    - **confirmed**: 已确认
    - **in_progress**: 进行中
    - **completed**: 已完成
    - **cancelled**: 已取消
    - **refunded**: 已退款

    返回分页列表，包含关联的咨询师信息
    """
    try:
        result = AppointmentService.get_user_appointments(
            db, user_id, status_filter, page, page_size
        )
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取预约列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预约列表失败: {str(e)}"
        )


@router_appointment.get("/counselor/list", summary="获取咨询师预约列表")
async def get_counselor_appointments(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取咨询师收到的预约列表

    支持状态筛选：
    - **pending**: 待确认
    - **confirmed**: 已确认
    - **in_progress**: 进行中
    - **completed**: 已完成
    - **cancelled**: 已取消
    - **refunded**: 已退款

    返回分页列表，包含预约的用户信息
    """
    try:
        result = AppointmentService.get_counselor_appointments(
            db, user_id, status_filter, page, page_size
        )
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取咨询师预约列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取咨询师预约列表失败: {str(e)}"
        )


@router_appointment.get("/{appointment_id}", summary="获取预约详情")
async def get_appointment_detail(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取预约订单详情

    包含完整的订单信息、咨询师信息和用户信息
    """
    try:
        appointment = AppointmentService.get_appointment_detail(db, appointment_id)

        # 验证访问权限
        if appointment.user_id != user_id:
            # 检查是否是咨询师
            from app.models.counselor import Counselor
            counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id,
                Counselor.id == appointment.counselor_id
            ).first()
            if not counselor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此订单"
                )

        return {
            "code": 200,
            "message": "获取成功",
            "data": appointment
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取预约详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预约详情失败: {str(e)}"
        )


@router_appointment.post("/{appointment_id}/cancel", summary="取消预约")
async def cancel_appointment(
    appointment_id: int,
    reason: Optional[str] = Query(None, description="取消原因"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消预约订单

    ⚠️ 只能取消状态为 pending/confirmed/in_progress 的订单

    已完成或已取消的订单无法取消
    """
    try:
        AppointmentService.cancel_appointment(db, user_id, appointment_id, reason)
        return {
            "code": 200,
            "message": "预约已取消",
            "data": {
                "appointment_id": appointment_id,
                "cancelled": True
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消预约失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消预约失败: {str(e)}"
        )


@router_appointment.post("/{appointment_id}/review", summary="提交咨询评价")
async def submit_review(
    appointment_id: int,
    review_data: ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交咨询评价

    ⚠️ 只能评价已完成的咨询

    评价内容包括：
    - **rating**: 评分（1-5星）
    - **tags**: 评价标签（可选）
    - **content**: 评价内容（可选）
    - **is_anonymous**: 是否匿名

    提交后会更新咨询师的评分统计
    """
    try:
        review = AppointmentService.submit_review(db, user_id, appointment_id, review_data)
        return {
            "code": 200,
            "message": "评价提交成功",
            "data": review
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"提交评价失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交评价失败: {str(e)}"
        )


# ==================== 咨询师申请接口 ====================

@router.post("/apply", summary="提交咨询师注册申请")
async def submit_counselor_application(
    application_data: CounselorRegisterRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交咨询师注册申请

    申请需要填写：
    - **基本信息**: 姓名、性别、职称
    - **专业信息**: 擅长领域、咨询方式、从业年限、学历、资质
    - **定价信息**: 各咨询方式价格（可选）
    - **详细信息**: 个人简介（必填）、咨询方法、成就荣誉

    提交后申请状态为 `pending`，等待管理员审核

    ⚠️ 如果之前申请被拒绝，可以重新提交申请
    """
    try:
        counselor = CounselorService.submit_counselor_application(
            db, user_id, application_data
        )
        return {
            "code": 200,
            "message": "申请提交成功，请等待管理员审核",
            "data": counselor
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"提交申请失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交申请失败: {str(e)}"
        )


@router.get("/application/status", summary="获取咨询师申请状态")
async def get_application_status(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的咨询师申请状态

    返回信息包括：
    - **has_applied**: 是否已申请
    - **application_status**: 申请状态（pending/approved/rejected）
    - **rejection_reason**: 拒绝原因（如果被拒绝）
    - **reviewed_at**: 审核时间
    - **counselor_id**: 咨询师ID（审核通过后）
    - **can_edit**: 是否可以编辑（只有pending状态可以编辑）
    """
    try:
        status_info = CounselorService.get_counselor_application_status(db, user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": status_info
        }
    except Exception as e:
        logger.error(f"获取申请状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取申请状态失败: {str(e)}"
        )


@router.get("/application/pending", summary="获取待审核申请列表（管理员）")
async def get_pending_applications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取待审核的咨询师申请列表（管理员专用）

    返回所有申请状态为 `pending` 的咨询师申请
    按申请时间升序排列（先申请的先审核）
    """
    try:
        result = CounselorService.get_pending_applications(db, page, page_size)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取待审核列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待审核列表失败: {str(e)}"
        )


@router.post("/application/{counselor_id}/review", summary="审核咨询师申请（管理员）")
async def review_application(
    counselor_id: int,
    action: str = Query(..., pattern=r'^(approve|reject)$', description="审核操作：approve通过/reject拒绝"),
    reason: Optional[str] = Query(None, description="拒绝原因（拒绝时必填）"),
    db: Session = Depends(get_db)
):
    """
    审核咨询师申请（管理员专用）

    - **approve**: 通过申请，咨询师状态变为 active
    - **reject**: 拒绝申请，需提供拒绝原因

    审核后：
    - 通过：咨询师账号激活，可以接单
    - 拒绝：咨询师可以重新提交申请
    """
    try:
        # TODO: 添加管理员权限验证
        # 临时使用固定管理员ID
        reviewer_id = 1

        if action == 'reject' and not reason:
            raise ValueError("拒绝申请时必须提供拒绝原因")

        result = CounselorService.review_counselor_application(
            db, counselor_id, action, reviewer_id, reason
        )

        action_text = "通过" if action == "approve" else "拒绝"
        return {
            "code": 200,
            "message": f"申请已{action_text}",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"审核申请失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核申请失败: {str(e)}"
        )
