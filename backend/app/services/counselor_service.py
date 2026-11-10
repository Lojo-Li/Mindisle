"""
咨询师预约服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import uuid
import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

from app.models.counselor import Counselor, Appointment, ConsultationReview, CounselorTimeSlot
from app.schemas.counselor import (
    CounselorResponse, CounselorListQuery, CounselorRegisterRequest, TimeSlot,
    AppointmentCreate, AppointmentResponse, AppointmentListResponse,
    ReviewCreate, ReviewResponse, ReviewListResponse,
    MessageResponse, MessageListResponse, SendMessageRequest,
    HandleOrderRequest, AddNoteRequest, FileUploadResponse,
    SlotPublishRequest
)


# 占用咨询师时段的有效预约状态；cancelled / refunded / completed 均释放时段
ACTIVE_APPOINTMENT_STATUSES = ('pending', 'confirmed', 'in_progress')
# 预约默认时长（分钟），与 Appointment.duration 保持一致
DEFAULT_APPOINTMENT_MINUTES = 60
# 按开始时间预筛查询窗口时向前回溯的最大分钟数，覆盖任意单条预约的时长
_MAX_APPOINTMENT_MINUTES = 24 * 60


def _appointment_interval(start: datetime, duration) -> tuple:
    """返回预约占用的半开区间 [start, end)。"""
    minutes = duration if duration and duration > 0 else DEFAULT_APPOINTMENT_MINUTES
    return start, start + timedelta(minutes=minutes)


def _intervals_overlap(a_start, a_end, b_start, b_end) -> bool:
    """半开区间重叠判断；首尾相接（a_end == b_start）不算冲突。"""
    return a_start < b_end and b_start < a_end


def _active_appointments_in_window(db: Session, counselor_id, window_start, window_end):
    """按开始时间预筛可能与 [window_start, window_end) 重叠的有效预约。

    只使用与数据库方言无关的范围过滤，精确的重叠判断在 _has_time_conflict 中完成，
    避免依赖 MySQL 专有的时间函数（项目同时支持 SQLite 本地模式）。
    """
    return db.query(Appointment).filter(
        Appointment.counselor_id == counselor_id,
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.appointment_date < window_end,
        Appointment.appointment_date >= window_start - timedelta(minutes=_MAX_APPOINTMENT_MINUTES),
    ).all()


def _has_time_conflict(db: Session, counselor_id, start, duration,
                       appointments=None, exclude_appointment_id=None) -> bool:
    """判断 [start, start+duration) 是否与同一咨询师已有的有效预约重叠。

    创建预约与可预约时段查询共用本函数，保证两处判定口径一致。
    appointments 允许调用方一次性预取，避免 slots 逐时段重复查询。
    """
    new_start, new_end = _appointment_interval(start, duration)
    if appointments is None:
        appointments = _active_appointments_in_window(db, counselor_id, new_start, new_end)
    for appt in appointments:
        if exclude_appointment_id is not None and appt.id == exclude_appointment_id:
            continue
        old_start, old_end = _appointment_interval(appt.appointment_date, appt.duration)
        if _intervals_overlap(new_start, new_end, old_start, old_end):
            return True
    return False


def _release_counselor_slot(db: Session, appointment: Appointment) -> None:
    """释放预约占用的排班时段（取消/拒单时调用）"""
    appt_start = appointment.appointment_date
    if appt_start.tzinfo is not None:
        appt_start = appt_start.replace(tzinfo=None)
    appt_end = appt_start + timedelta(minutes=appointment.duration or 60)
    booked_slot = db.query(CounselorTimeSlot).filter(
        CounselorTimeSlot.counselor_id == appointment.counselor_id,
        CounselorTimeSlot.slot_date == appt_start.date(),
        CounselorTimeSlot.status == 'booked',
        CounselorTimeSlot.start_time <= appt_start.time(),
        CounselorTimeSlot.end_time >= appt_end.time()
    ).first()
    if booked_slot:
        booked_slot.status = 'available'


class CounselorService:
    """咨询师服务"""

    @staticmethod
    def get_counselor_list(db: Session, query: CounselorListQuery) -> Dict[str, Any]:
        """获取咨询师列表"""
        # 构建查询
        q = db.query(Counselor).filter(
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        )

        # 关键词搜索
        if query.keyword:
            q = q.filter(
                or_(
                    Counselor.name.contains(query.keyword),
                    Counselor.specialties.contains(query.keyword),
                    Counselor.bio.contains(query.keyword)
                )
            )

        # 擅长领域筛选（支持多选）
        if query.specialties and len(query.specialties) > 0:
            specialty_conditions = []
            for specialty in query.specialties:
                if specialty.strip():
                    specialty_conditions.append(Counselor.specialties.contains(specialty.strip()))
            if specialty_conditions:
                q = q.filter(or_(*specialty_conditions))

        # 咨询方式筛选（支持多选）
        if query.consultation_types and len(query.consultation_types) > 0:
            type_conditions = []
            for consult_type in query.consultation_types:
                if consult_type.strip():
                    type_conditions.append(Counselor.consultation_types.contains(consult_type.strip()))
            if type_conditions:
                q = q.filter(or_(*type_conditions))

        # 价格范围筛选
        if query.price_min is not None:
            q = q.filter(
                or_(
                    Counselor.price_video >= query.price_min,
                    Counselor.price_voice >= query.price_min,
                    Counselor.price_offline >= query.price_min
                )
            )
        if query.price_max is not None:
            q = q.filter(
                or_(
                    Counselor.price_video <= query.price_max,
                    Counselor.price_voice <= query.price_max,
                    Counselor.price_offline <= query.price_max
                )
            )

        # 排序
        if query.sort == "rating":
            q = q.order_by(desc(Counselor.rating), desc(Counselor.review_count))
        elif query.sort == "orders":
            q = q.order_by(desc(Counselor.consultation_count))
        elif query.sort == "price-asc":
            q = q.order_by(Counselor.price_video.asc())
        else:  # default
            q = q.order_by(desc(Counselor.rating), desc(Counselor.consultation_count))

        # 总数
        total = q.count()

        # 分页
        offset = (query.page - 1) * query.page_size
        counselors = q.offset(offset).limit(query.page_size).all()

        # 转换为响应格式（并标注是否还有可预约时段）
        availability = CounselorService._availability_map(db, [c.id for c in counselors])
        items = [
            CounselorResponse.model_validate(c).model_copy(
                update={"has_available_slot": availability.get(c.id, True)}
            )
            for c in counselors
        ]

        return {
            "total": total,
            "items": items,
            "page": query.page,
            "page_size": query.page_size
        }

    @staticmethod
    def _availability_map(db: Session, counselor_ids: List[int]) -> Dict[int, bool]:
        """批量判断咨询师是否还有可预约时段

        - 存在未来 available 的已发布时段 → 可预约
        - 从未发布过任何时段（老数据）→ 沿用默认 09:00-18:00 逻辑，视为可预约
        - 发布过但全部已被预约 → 不可预约
        """
        ids = [cid for cid in counselor_ids if cid is not None]
        if not ids:
            return {}

        rows = db.query(
            CounselorTimeSlot.counselor_id,
            CounselorTimeSlot.status,
            func.count(CounselorTimeSlot.id)
        ).filter(
            CounselorTimeSlot.counselor_id.in_(ids),
            CounselorTimeSlot.slot_date >= date.today()
        ).group_by(
            CounselorTimeSlot.counselor_id, CounselorTimeSlot.status
        ).all()

        available_ids, published_ids = set(), set()
        for cid, status, _count in rows:
            published_ids.add(cid)
            if status == 'available':
                available_ids.add(cid)

        return {
            cid: (cid in available_ids) or (cid not in published_ids)
            for cid in ids
        }

    @staticmethod
    def get_counselor_detail(db: Session, counselor_id: int) -> CounselorResponse:
        """获取咨询师详情"""
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False
        ).first()

        if not counselor:
            raise ValueError("咨询师不存在")

        available = CounselorService._availability_map(db, [counselor.id])
        return CounselorResponse.model_validate(counselor).model_copy(
            update={"has_available_slot": available.get(counselor.id, True)}
        )

    @staticmethod
    def get_available_slots(
        db: Session,
        counselor_id: int,
        appointment_date: str
    ) -> List[TimeSlot]:
        """获取可预约时段"""
        # 验证咨询师
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        ).first()
        if not counselor:
            raise ValueError("咨询师不存在")

        # 解析日期
        try:
            appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("日期格式错误")

        # 优先使用咨询师发布的时段（排班）；未发布过排班时回退到默认 09:00-18:00
        published_slots = db.query(CounselorTimeSlot).filter(
            CounselorTimeSlot.counselor_id == counselor_id,
            CounselorTimeSlot.slot_date == appt_date,
            CounselorTimeSlot.status != 'disabled'
        ).order_by(CounselorTimeSlot.start_time).all()

        if published_slots:
            return [
                TimeSlot(
                    time=f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}",
                    available=(slot.status == 'available'),
                    price=counselor.price_video or counselor.price_voice or counselor.price_offline
                )
                for slot in published_slots
            ]

        day_start = datetime.combine(appt_date, datetime.min.time())
        active_appointments = _active_appointments_in_window(
            db, counselor_id, day_start, day_start + timedelta(days=1))

        # 定义时段（09:00-18:00，每小时一个时段）
        time_slots = []
        for hour in range(9, 19):
            slot_time = f"{hour:02d}:00-{hour+1:02d}:00"
            slot_start = day_start.replace(hour=hour)

            # 检查该时段是否与已有预约的 [start, start+duration) 重叠
            occupied = _has_time_conflict(
                db, counselor_id, slot_start, DEFAULT_APPOINTMENT_MINUTES,
                appointments=active_appointments)

            # 获取该时段价格
            price = None
            if counselor.price_video and counselor.consultation_types and 'video' in counselor.consultation_types:
                price = counselor.price_video
            elif counselor.price_voice and counselor.consultation_types and 'voice' in counselor.consultation_types:
                price = counselor.price_voice

            time_slots.append(TimeSlot(
                time=slot_time,
                available=not occupied,
                price=price
            ))

        return time_slots

    @staticmethod
    def get_counselor_reviews(
        db: Session,
        counselor_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取咨询师评价列表"""
        # 验证咨询师
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False
        ).first()
        if not counselor:
            raise ValueError("咨询师不存在")

        # 查询评价
        q = db.query(ConsultationReview).filter(
            ConsultationReview.counselor_id == counselor_id
        ).order_by(ConsultationReview.created_at.desc())

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        reviews = q.offset(offset).limit(page_size).all()

        # 转换为响应格式
        items = []
        for review in reviews:
            review_data = ReviewResponse.model_validate(review)
            # 如果不匿名，添加用户信息
            if not review.is_anonymous:
                from app.models.user import User
                user = db.query(User).filter(User.id == review.user_id).first()
                if user:
                    review_data.user_name = user.nickname or user.email.split('@')[0]
                    review_data.user_avatar = user.avatar
            items.append(review_data)

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def submit_counselor_application(
        db: Session,
        user_id: int,
        application_data: CounselorRegisterRequest
    ) -> CounselorResponse:
        """提交咨询师注册申请"""
        from app.models.user import User

        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 检查用户是否已经是咨询师
        existing = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()
        if existing:
            if existing.application_status == 'pending':
                raise ValueError("您的申请正在审核中，请耐心等待")
            elif existing.application_status == 'rejected':
                # 被拒绝的可以重新申请，更新原记录
                existing.application_status = 'pending'
                existing.rejection_reason = None
                existing.reviewed_at = None
                existing.reviewed_by = None
                existing.status = 'pending_review'
            else:
                raise ValueError("您已经是咨询师，无需重复申请")

        # 将列表转换为逗号分隔的字符串
        specialties_str = ','.join(application_data.specialties)
        consultation_types_str = ','.join(application_data.consultation_types)

        # 创建或更新咨询师记录
        if existing and existing.application_status == 'rejected':
            # 更新被拒绝的申请
            counselor = existing
            counselor.name = application_data.name
            counselor.gender = application_data.gender
            counselor.title = application_data.title
            counselor.specialties = specialties_str
            counselor.consultation_types = consultation_types_str
            counselor.experience_years = application_data.experience_years
            counselor.education = application_data.education
            counselor.qualifications = application_data.qualifications
            counselor.price_video = application_data.price_video
            counselor.price_voice = application_data.price_voice
            counselor.price_offline = application_data.price_offline
            counselor.bio = application_data.bio
            counselor.approach = application_data.approach
            counselor.achievements = application_data.achievements
            counselor.updated_at = datetime.now()
        else:
            # 创建新的申请
            counselor = Counselor(
                user_id=user_id,
                name=application_data.name,
                gender=application_data.gender,
                title=application_data.title,
                specialties=specialties_str,
                consultation_types=consultation_types_str,
                experience_years=application_data.experience_years,
                education=application_data.education,
                qualifications=application_data.qualifications,
                price_video=application_data.price_video,
                price_voice=application_data.price_voice,
                price_offline=application_data.price_offline,
                bio=application_data.bio,
                approach=application_data.approach,
                achievements=application_data.achievements,
                status='pending_review',
                application_status='pending',
                rating=5.0,
                review_count=0,
                consultation_count=0
            )
            db.add(counselor)

        db.commit()
        db.refresh(counselor)

        return CounselorResponse.model_validate(counselor)

    @staticmethod
    def get_counselor_application_status(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """获取用户的咨询师申请状态"""
        counselor = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()

        if not counselor:
            return {
                "has_applied": False,
                "application_status": None,
                "can_edit": True
            }

        # pending状态可以编辑
        can_edit = counselor.application_status == 'pending'

        return {
            "has_applied": True,
            "application_status": counselor.application_status,
            "rejection_reason": counselor.rejection_reason,
            "reviewed_at": counselor.reviewed_at,
            "counselor_id": counselor.id if counselor.application_status == 'approved' else None,
            "can_edit": can_edit
        }

    @staticmethod
    def get_pending_applications(
        db: Session,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取待审核的咨询师申请列表（管理员用）"""
        from app.models.user import User

        q = db.query(Counselor, User.email).outerjoin(
            User, User.id == Counselor.user_id
        ).filter(
            Counselor.application_status == 'pending',
            Counselor.is_deleted == False
        ).order_by(Counselor.created_at.asc())

        total = q.count()
        offset = (page - 1) * page_size
        rows = q.offset(offset).limit(page_size).all()

        items = []
        for counselor, user_email in rows:
            # user_email 不是 Counselor 模型字段，需显式回填
            counselor_data = CounselorResponse.model_validate(counselor).model_copy(
                update={"user_email": user_email}
            )
            items.append(counselor_data)

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def review_counselor_application(
        db: Session,
        counselor_id: int,
        action: str,  # approve, reject
        reviewer_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """审核咨询师申请"""
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False
        ).first()

        if not counselor:
            raise ValueError("咨询师申请不存在")

        if counselor.application_status != 'pending':
            raise ValueError("该申请已处理，无法重复审核")

        if action == 'approve':
            # 通过审核
            counselor.application_status = 'approved'
            counselor.status = 'active'
            counselor.is_verified = True
        elif action == 'reject':
            # 拒绝申请
            counselor.application_status = 'rejected'
            counselor.status = 'inactive'
            counselor.rejection_reason = reason
        else:
            raise ValueError("无效的审核操作")

        counselor.reviewed_at = datetime.now()
        counselor.reviewed_by = reviewer_id

        db.commit()
        db.refresh(counselor)

        # 发送审核结果邮件
        try:
            from app.services.email_service import EmailService
            from app.models.user import User

            # 获取用户邮箱
            user = db.query(User).filter(User.id == counselor.user_id).first()
            if user and user.email:
                try:
                    if action == 'approve':
                        EmailService.send_counselor_approval(
                            email=user.email,
                            name=counselor.name
                        )
                    elif action == 'reject':
                        EmailService.send_counselor_rejection(
                            email=user.email,
                            name=counselor.name,
                            reason=reason
                        )
                except Exception as e:
                    logger.error(f"发送审核邮件失败: {e}")
        except Exception as e:
            logger.error(f"发送审核邮件时出错: {e}")

        return {
            "counselor_id": counselor.id,
            "application_status": counselor.application_status,
            "action": action,
            "reviewed_at": counselor.reviewed_at
        }

    # ==================== 管理后台方法 ====================

    @staticmethod
    def get_admin_counselors(
        db: Session,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取咨询师列表（管理后台）

        Args:
            db: 数据库会话
            keyword: 搜索关键词（姓名/邮箱/手机号）
            status: 状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            包含咨询师列表和总数的字典
        """
        # 构建查询（关联 users 表获取邮箱和手机号）
        from app.models.user import User

        q = db.query(Counselor).filter(Counselor.is_deleted == False)

        # 关键词搜索（只搜索姓名）
        if keyword:
            q = q.filter(Counselor.name.contains(keyword))

        # 状态筛选
        if status:
            q = q.filter(Counselor.status == status)

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        counselors = q.order_by(desc(Counselor.created_at)).offset(offset).limit(page_size).all()

        # 转换为字典格式
        items = []
        for counselor in counselors:
            # 获取关联的用户信息
            user = None
            if counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()

            # 解析擅长领域
            specialties = counselor.specialties if counselor.specialties else []
            if isinstance(specialties, str):
                specialties = specialties.split(',')

            items.append({
                "id": counselor.id,
                "name": counselor.name,
                "email": user.email if user else "",
                "phone": user.phone if user else "",
                "specialties": specialties,
                "status": counselor.status,
                "is_active": counselor.is_verified,  # 前端期望的字段名
                "createTime": counselor.created_at.strftime("%Y-%m-%d %H:%M:%S") if counselor.created_at else ""
            })

        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size
        }

    @staticmethod
    def toggle_counselor_status(db: Session, counselor_id: int, active: bool) -> bool:
        """
        切换咨询师状态（启用/禁用）

        Args:
            db: 数据库会话
            counselor_id: 咨询师ID
            active: 是否启用

        Returns:
            是否操作成功
        """
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False
        ).first()

        if not counselor:
            raise ValueError("咨询师不存在")

        counselor.is_verified = active
        db.commit()

        return True


class AppointmentService:
    """预约服务"""

    @staticmethod
    def create_appointment(
        db: Session,
        user_id: int,
        appointment_data: AppointmentCreate
    ) -> AppointmentResponse:
        """创建预约"""
        # 验证咨询师。在同一事务内锁定该咨询师行，串行化同一咨询师的并发创建，
        # 防止两个请求同时通过时段校验后各自插入（多 worker / 多线程部署）。
        # SQLite 不支持 FOR UPDATE，SQLAlchemy 会自动忽略，本地模式不受影响。
        counselor = db.query(Counselor).filter(
            Counselor.id == appointment_data.counselor_id,
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        ).with_for_update().first()
        if not counselor:
            raise ValueError("咨询师不存在")

        # 解析预约时间。保持原项目使用的无时区本地时间格式，
        # 带时区偏移的输入一律返回 400，避免 aware/naive 比较触发 500。
        try:
            appt_datetime = datetime.fromisoformat(appointment_data.appointment_date.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            raise ValueError("日期时间格式错误")
        if appt_datetime.tzinfo is not None:
            raise ValueError("日期时间格式错误")

        # 检查预约时间不能是过去
        if appt_datetime < datetime.now():
            raise ValueError("预约时间不能是过去的时间")

        # 预约时长固定 60 分钟
        appt_end = appt_datetime + timedelta(minutes=60)

        # 检查预约区间 [start, start+duration) 是否与已有有效预约重叠
        # 与 /counselor/{id}/slots 共用 _has_time_conflict，保证两处判定口径一致
        if _has_time_conflict(db, appointment_data.counselor_id,
                              appt_datetime, DEFAULT_APPOINTMENT_MINUTES):
            raise ValueError("该时段已被预约")

        # 若咨询师已发布排班时段，预约必须完整落在某个 available 时段内，并锁定该时段
        slot_to_book = None
        published_slots = db.query(CounselorTimeSlot).filter(
            CounselorTimeSlot.counselor_id == appointment_data.counselor_id,
            CounselorTimeSlot.slot_date == appt_datetime.date(),
            CounselorTimeSlot.status != 'disabled'
        ).all()
        if published_slots:
            for slot in published_slots:
                slot_start = datetime.combine(appt_datetime.date(), slot.start_time)
                slot_end = datetime.combine(appt_datetime.date(), slot.end_time)
                if slot_start <= appt_datetime and appt_end <= slot_end:
                    slot_to_book = slot
                    break
            if slot_to_book is None:
                raise ValueError("咨询师未开放该时段，请从已发布的可预约时段中选择")
            if slot_to_book.status != 'available':
                raise ValueError("该时段已被预约")

        # 公益活动：所有咨询免费，不再计算/收取任何费用
        # 这里仅保留"咨询师是否支持该咨询方式"的校验
        supported_types = [t.strip() for t in (counselor.consultation_types or '').split(',') if t.strip()]
        if appointment_data.consultation_type not in supported_types:
            raise ValueError(f"咨询师暂不支持{appointment_data.consultation_type}咨询方式")
        price = 0

        # 生成预约编号
        appointment_no = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

        # 创建预约
        appointment = Appointment(
            user_id=user_id,
            counselor_id=appointment_data.counselor_id,
            appointment_no=appointment_no,
            consultation_type=appointment_data.consultation_type,
            appointment_date=appt_datetime,
            duration=DEFAULT_APPOINTMENT_MINUTES,
            user_name=appointment_data.user_name,
            user_contact=appointment_data.user_contact,
            problem_description=appointment_data.problem_description,
            price=price,
            paid_amount=0,
            status='pending'
        )

        db.add(appointment)

        # 锁定已发布的排班时段
        if slot_to_book is not None:
            slot_to_book.status = 'booked'

        db.commit()
        db.refresh(appointment)

        # 发送预约成功邮件
        try:
            from app.services.email_service import EmailService
            from app.models.user import User

            # 格式化预约时间（用户与咨询师两类邮件共用，无条件定义）
            appointment_date_str = appt_datetime.strftime("%Y-%m-%d")
            appointment_time_str = appt_datetime.strftime("%H:%M")

            # 获取用户信息
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                # 发送给用户
                try:
                    EmailService.send_appointment_confirmation_user(
                        email=user.email,
                        nickname=user.nickname or "用户",
                        counselor_name=counselor.name,
                        appointment_date=appointment_date_str,
                        appointment_time=appointment_time_str,
                        consultation_type=appointment_data.consultation_type,
                        appointment_no=appointment_no
                    )
                except Exception as e:
                    logger.error(f"发送用户预约邮件失败: {e}")

            # 发送给咨询师。counselors 表无 email 列，邮箱取自关联的 users 表
            counselor_user = db.query(User).filter(User.id == counselor.user_id).first()
            counselor_email = counselor_user.email if counselor_user else None
            if counselor_email:
                try:
                    EmailService.send_appointment_confirmation_counselor(
                        email=counselor_email,
                        counselor_name=counselor.name,
                        user_name=appointment_data.user_name or (user.nickname if user else "用户"),
                        appointment_date=appointment_date_str,
                        appointment_time=appointment_time_str,
                        consultation_type=appointment_data.consultation_type,
                        appointment_no=appointment_no,
                        problem_description=appointment_data.problem_description or ""
                    )
                except Exception as e:
                    logger.error(f"发送咨询师预约邮件失败: {e}")
        except ImportError:
            logger.warning("邮件服务未导入，跳过邮件发送")
        except Exception as e:
            logger.error(f"发送预约邮件时出错: {e}")

        # 通知咨询师有新预约
        try:
            from app.services.notification_service import NotificationService
            counselor_user = db.query(User).filter(User.id == counselor.user_id).first()
            if counselor_user:
                NotificationService.notify_new_appointment(
                    db, counselor.user_id, appointment.id,
                    appointment_data.user_name or "用户",
                    appt_datetime.strftime('%Y-%m-%d %H:%M')
                )
        except Exception as e:
            logger.error(f"发送新预约通知失败: {e}")

        return AppointmentService.get_appointment_detail(db, appointment.id)

    @staticmethod
    def get_user_appointments(
        db: Session,
        user_id: int,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取用户预约列表"""
        from sqlalchemy.orm import selectinload

        q = db.query(Appointment).filter(Appointment.user_id == user_id)

        # 状态筛选
        if status_filter:
            q = q.filter(Appointment.status == status_filter)

        # 按创建时间倒序
        q = q.order_by(Appointment.created_at.desc())

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        # 使用 selectinload 主动加载 counselor 关系
        appointments = q.options(selectinload(Appointment.counselor)).offset(offset).limit(page_size).all()

        # 转换为响应格式
        items = []
        for appt in appointments:
            appt_data = AppointmentResponse.model_validate(appt)
            # 添加咨询师信息
            if appt.counselor:
                appt_data.counselor = CounselorResponse.model_validate(appt.counselor)
            items.append(appt_data)

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_appointment_detail(db: Session, appointment_id: int) -> AppointmentResponse:
        """获取预约详情"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            raise ValueError("预约不存在")

        appt_data = AppointmentResponse.model_validate(appointment)

        # 添加咨询师信息
        if appointment.counselor:
            appt_data.counselor = CounselorResponse.model_validate(appointment.counselor)

        # 添加用户信息
        from app.models.user import User
        user = db.query(User).filter(User.id == appointment.user_id).first()
        if user:
            appt_data.user_info = {
                "id": user.id,
                "nickname": user.nickname,
                "email": user.email,
                "phone": user.phone,
                "avatar": user.avatar
            }

        return appt_data

    @staticmethod
    def get_counselor_appointments(
        db: Session,
        counselor_id: int,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取咨询师收到的预约列表"""
        from app.models.user import User

        # 先获取咨询师ID（通过user_id）。非咨询师直接拒绝访问
        counselor = db.query(Counselor).filter(Counselor.user_id == counselor_id).first()
        if not counselor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅咨询师可访问")

        # 查询该咨询师的预约订单（一并取出下单用户，Appointment 与 User 之间无 relationship）
        q = db.query(Appointment, User).outerjoin(
            User, User.id == Appointment.user_id
        ).filter(Appointment.counselor_id == counselor.id)

        # 状态筛选
        if status_filter:
            q = q.filter(Appointment.status == status_filter)

        # 按创建时间倒序
        q = q.order_by(Appointment.created_at.desc())

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        appointments = q.offset(offset).limit(page_size).all()

        # 转换为响应格式（用户信息随查询一并取出，避免 N+1）
        items = []
        for appt, user in appointments:
            user_info = None
            if user:
                user_info = {
                    "id": user.id,
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone
                }
            items.append(
                AppointmentResponse.model_validate(appt).model_copy(
                    update={"user_info": user_info}
                )
            )

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def cancel_appointment(db: Session, user_id: int, appointment_id: int, reason: Optional[str] = None) -> bool:
        """取消预约"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            raise ValueError("预约不存在")
        if appointment.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作此预约")

        if appointment.status in ['completed', 'cancelled', 'refunded']:
            raise ValueError(f"预约状态为{appointment.status}，无法取消")

        # 更新状态
        appointment.status = 'cancelled'
        appointment.cancel_reason = reason
        appointment.cancelled_at = datetime.now()

        # 释放被锁定的排班时段
        _release_counselor_slot(db, appointment)

        db.commit()

        # 发送取消通知邮件
        try:
            from app.services.email_service import EmailService
            from app.models.user import User

            # 格式化预约时间
            appointment_date_str = appointment.appointment_date.strftime("%Y-%m-%d")
            appointment_time_str = appointment.appointment_date.strftime("%H:%M")

            # 通知用户
            user = db.query(User).filter(User.id == appointment.user_id).first()
            if user and user.email:
                try:
                    EmailService.send_appointment_cancelled(
                        email=user.email,
                        nickname=user.nickname or "用户",
                        appointment_date=appointment_date_str,
                        appointment_time=appointment_time_str,
                        reason=reason or "您已取消预约"
                    )
                except Exception as e:
                    logger.error(f"发送用户取消邮件失败: {e}")

            # 通知咨询师。邮箱取自关联的 users 表
            counselor_email = None
            if appointment.counselor:
                counselor_user = db.query(User).filter(
                    User.id == appointment.counselor.user_id
                ).first()
                counselor_email = counselor_user.email if counselor_user else None
            if counselor_email:
                try:
                    EmailService.send_appointment_cancelled(
                        email=counselor_email,
                        nickname=appointment.counselor.name,
                        appointment_date=appointment_date_str,
                        appointment_time=appointment_time_str,
                        reason=reason or "用户已取消预约"
                    )
                except Exception as e:
                    logger.error(f"发送咨询师取消邮件失败: {e}")
        except Exception as e:
            logger.error(f"发送取消邮件时出错: {e}")

        # 发送通知
        try:
            from app.services.notification_service import NotificationService
            user = db.query(User).filter(User.id == user_id).first()
            user_name = user.nickname if user else "用户"
            # 通知咨询师
            if appointment.counselor:
                counselor_user = db.query(User).filter(User.id == appointment.counselor.user_id).first()
                if counselor_user:
                    NotificationService.notify_appointment_cancelled(
                        db, counselor_user.id, appointment_id, user_name
                    )
            # 通知用户（确认取消）
            NotificationService.notify_appointment_cancelled(
                db, user_id, appointment_id, "您"
            )
        except Exception as e:
            logger.error(f"发送取消通知失败: {e}")

        return True

    @staticmethod
    def submit_review(
        db: Session,
        user_id: int,
        appointment_id: int,
        review_data: ReviewCreate
    ) -> ReviewResponse:
        """提交评价"""
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appointment:
            raise ValueError("预约不存在")
        if appointment.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作此预约")

        if appointment.status != 'completed':
            raise ValueError("只能评价已完成的咨询")

        # 检查是否已评价
        existing = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == appointment_id
        ).first()
        if existing:
            raise ValueError("已经评价过该咨询")

        # 创建评价
        review = ConsultationReview(
            appointment_id=appointment_id,
            user_id=user_id,
            counselor_id=appointment.counselor_id,
            rating=review_data.rating,
            tags=','.join(review_data.tags) if review_data.tags else None,
            content=review_data.content,
            is_anonymous=review_data.is_anonymous
        )

        db.add(review)
        # 会话工厂为 autoflush=False，必须先 flush 把新评价写入当前事务，
        # 否则下方聚合查询统计不到本次评价，导致 rating / review_count 滞后
        db.flush()

        # 更新咨询师统计
        counselor = db.query(Counselor).filter(
            Counselor.id == appointment.counselor_id
        ).first()
        if counselor:
            # 重新计算平均评分
            all_reviews = db.query(ConsultationReview).filter(
                ConsultationReview.counselor_id == counselor.id
            ).all()
            if all_reviews:
                counselor.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            counselor.review_count = len(all_reviews)

        db.commit()
        db.refresh(review)

        return ReviewResponse.model_validate(review)


class ConsultationService:
    """咨询对话服务"""

    @staticmethod
    def get_counselor_orders(
        db: Session,
        counselor_id: int,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取咨询师订单列表"""
        q = db.query(Appointment).filter(Appointment.counselor_id == counselor_id)

        # 状态筛选
        if status_filter:
            q = q.filter(Appointment.status == status_filter)

        # 按创建时间倒序
        q = q.order_by(Appointment.created_at.desc())

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        appointments = q.offset(offset).limit(page_size).all()

        # 转换为响应格式
        items = []
        for appt in appointments:
            # 转换为字典
            appt_dict = {
                "id": appt.id,
                "appointment_no": appt.appointment_no,
                "counselor_id": appt.counselor_id,
                "consultation_type": appt.consultation_type,
                "appointment_date": appt.appointment_date,
                "duration": appt.duration,
                "price": appt.price,
                "paid_amount": appt.paid_amount,
                "status": appt.status,
                "user_name": appt.user_name,
                "user_contact": appt.user_contact,
                "problem_description": appt.problem_description,
                "counselor_notes": appt.counselor_notes,
                "created_at": appt.created_at,
                "confirmed_at": appt.confirmed_at,
                "completed_at": appt.completed_at,
                "cancelled_at": appt.cancelled_at
            }

            # 添加咨询师信息
            if appt.counselor:
                counselor_dict = CounselorResponse.model_validate(appt.counselor).model_dump()
                appt_dict["counselor"] = counselor_dict

            # 添加用户信息
            from app.models.user import User
            user = db.query(User).filter(User.id == appt.user_id).first()
            if user:
                appt_dict["user_info"] = {
                    "id": user.id,
                    "nickname": user.nickname,
                    "email": user.email,
                    "phone": user.phone,
                    "avatar": user.avatar
                }

            items.append(appt_dict)

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def handle_order(
        db: Session,
        counselor_id: int,
        appointment_id: int,
        action: str,
        reason: Optional[str] = None
    ) -> bool:
        """处理预约订单"""
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.counselor_id == counselor_id
        ).first()

        if not appointment:
            raise ValueError("预约不存在")

        if appointment.status != 'pending':
            raise ValueError(f"预约状态为{appointment.status}，无法处理")

        if action == 'agree':
            appointment.status = 'confirmed'
            appointment.confirmed_at = datetime.now()

            # 发送系统消息通知用户
            ConsultationService._send_system_message(
                db, appointment_id,
                f"咨询师已确认您的预约，咨询时间：{appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}"
            )
            # 发送通知
            from app.services.notification_service import NotificationService
            counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
            NotificationService.notify_appointment_confirmed(
                db, appointment.user_id, appointment_id,
                counselor.name if counselor else "咨询师",
                appointment.appointment_date.strftime('%Y-%m-%d %H:%M')
            )
        elif action == 'reject':
            appointment.status = 'cancelled'
            appointment.cancel_reason = reason
            appointment.cancelled_at = datetime.now()
            # 释放被锁定的排班时段
            _release_counselor_slot(db, appointment)

            # 发送系统消息通知用户
            ConsultationService._send_system_message(
                db, appointment_id,
                f"抱歉，咨询师拒绝了您的预约。原因：{reason or '暂无'}"
            )
            # 发送通知
            from app.services.notification_service import NotificationService
            counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
            NotificationService.notify_appointment_rejected(
                db, appointment.user_id, appointment_id,
                counselor.name if counselor else "咨询师", reason
            )
        else:
            raise ValueError("无效的操作")

        db.commit()
        return True

    @staticmethod
    def get_messages(
        db: Session,
        appointment_id: int,
        user_id: int,
        user_type: str,
        last_id: Optional[int] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取对话消息"""
        from app.models.counselor import ConsultationMessage

        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        if not appointment:
            raise ValueError("预约不存在")

        # 验证权限
        if user_type == 'user' and appointment.user_id != user_id:
            raise ValueError("无权访问此对话")
        if user_type == 'counselor' and appointment.counselor_id != user_id:
            raise ValueError("无权访问此对话")

        # 构建查询
        q = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id == appointment_id
        ).order_by(ConsultationMessage.created_at.asc())

        # 增量获取（从last_id之后）
        if last_id:
            q = q.filter(ConsultationMessage.id > last_id)

        # 获取消息
        messages = q.limit(limit).all()

        # 标记对方发送的消息为已读
        for msg in messages:
            if msg.sender_type != user_type and not msg.is_read:
                msg.is_read = True
                msg.read_at = datetime.now()

        db.commit()

        # 总数
        total = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id == appointment_id
        ).count()

        # 转换为响应格式
        items = [MessageResponse.model_validate(msg) for msg in messages]

        return {
            "total": total,
            "items": items,
            "has_more": len(messages) == limit
        }

    @staticmethod
    def send_message(
        db: Session,
        appointment_id: int,
        sender_id: int,
        sender_type: str,
        message_data: SendMessageRequest
    ) -> MessageResponse:
        """发送消息"""
        from app.models.counselor import ConsultationMessage

        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        if not appointment:
            raise ValueError("预约不存在")

        # 验证权限
        if sender_type == 'user' and appointment.user_id != sender_id:
            raise ValueError("无权发送消息")
        if sender_type == 'counselor' and appointment.counselor_id != sender_id:
            raise ValueError("无权发送消息")

        # 验证状态
        if appointment.status not in ['confirmed', 'in_progress']:
            raise ValueError("预约状态不允许发送消息")

        # 如果是第一条消息，更新预约状态为进行中
        if appointment.status == 'confirmed':
            appointment.status = 'in_progress'

        # 创建消息
        message = ConsultationMessage(
            appointment_id=appointment_id,
            sender_id=sender_id,
            sender_type=sender_type,
            message_type=message_data.message_type,
            content=message_data.content,
            file_url=message_data.file_url,
            file_name=message_data.file_name,
            file_size=message_data.file_size
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        # 通知对方有新消息
        try:
            from app.services.notification_service import NotificationService
            from app.models.user import User
            if sender_type == 'user':
                # 用户发消息 → 通知咨询师，发送者名为用户昵称
                sender_user = db.query(User).filter(User.id == sender_id).first()
                sender_name = sender_user.nickname if sender_user else "用户"
                counselor = db.query(Counselor).filter(Counselor.id == appointment.counselor_id).first()
                if counselor:
                    NotificationService.notify_new_message(
                        db, counselor.user_id, appointment_id,
                        sender_name, message_data.content or "[文件]"
                    )
            else:
                # 咨询师发消息 → 通知用户，发送者名为咨询师姓名
                counselor = db.query(Counselor).filter(Counselor.id == sender_id).first()
                sender_name = counselor.name if counselor else "咨询师"
                NotificationService.notify_new_message(
                    db, appointment.user_id, appointment_id,
                    sender_name, message_data.content or "[文件]"
                )
        except Exception as e:
            logger.error(f"发送消息通知失败: {e}")

        return MessageResponse.model_validate(message)

    @staticmethod
    def upload_file(file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """上传文件"""
        # 验证文件类型
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'audio/mpeg', 'audio/wav'
        ]
        if content_type not in allowed_types:
            raise ValueError("不支持的文件类型")

        # 验证文件大小（10MB）
        max_size = 10 * 1024 * 1024
        if len(file_data) > max_size:
            raise ValueError("文件大小不能超过 10MB")

        # 创建上传目录
        from pathlib import Path
        upload_dir = Path("uploads/consultation")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名
        import uuid
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = upload_dir / unique_filename

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_data)

        # 返回文件信息
        return {
            "file_url": f"/uploads/consultation/{unique_filename}",
            "file_name": filename,
            "file_size": len(file_data)
        }

    @staticmethod
    def end_consultation(
        db: Session,
        appointment_id: int,
        user_id: int,
        user_type: str
    ) -> bool:
        """结束咨询"""
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        if not appointment:
            raise ValueError("预约不存在")

        # 验证权限
        if user_type == 'user' and appointment.user_id != user_id:
            raise ValueError("无权操作")
        if user_type == 'counselor' and appointment.counselor_id != user_id:
            raise ValueError("无权操作")

        # 验证状态
        if appointment.status != 'in_progress':
            raise ValueError("只能结束进行中的咨询")

        # 更新状态
        appointment.status = 'completed'
        appointment.completed_at = datetime.now()

        # 发送系统消息
        ConsultationService._send_system_message(
            db, appointment_id,
            "咨询已结束，感谢您的使用！"
        )

        # 通知用户咨询已完成
        try:
            from app.services.notification_service import NotificationService
            counselor = db.query(Counselor).filter(Counselor.id == appointment.counselor_id).first()
            NotificationService.notify_appointment_completed(
                db, appointment.user_id, appointment_id,
                counselor.name if counselor else "咨询师"
            )
        except Exception as e:
            logger.error(f"发送咨询完成通知失败: {e}")

        db.commit()
        return True

    @staticmethod
    def add_note(
        db: Session,
        appointment_id: int,
        counselor_id: int,
        note: str
    ) -> bool:
        """添加咨询备注"""
        # 验证预约
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.counselor_id == counselor_id
        ).first()
        if not appointment:
            raise ValueError("预约不存在或无权操作")

        # 添加备注
        appointment.counselor_notes = note
        db.commit()

        return True

    @staticmethod
    def _send_system_message(db: Session, appointment_id: int, content: str):
        """发送系统消息"""
        from app.models.counselor import ConsultationMessage

        message = ConsultationMessage(
            appointment_id=appointment_id,
            sender_id=0,  # 系统消息
            sender_type='counselor',
            message_type='system',
            content=content
        )
        db.add(message)



class ScheduleService:
    """咨询师排班服务：时段发布、查询与删除（含冲突校验）"""

    @staticmethod
    def _get_counselor_by_user(db: Session, user_id: int) -> Counselor:
        """通过登录用户 ID 获取咨询师档案"""
        counselor = db.query(Counselor).filter(
            Counselor.user_id == user_id,
            Counselor.is_deleted == False
        ).first()
        if not counselor:
            raise ValueError("未找到咨询师档案，请先完成咨询师入驻申请")
        return counselor

    @staticmethod
    def publish_slots(db: Session, user_id: int, request: SlotPublishRequest) -> Dict[str, Any]:
        """
        批量发布可预约时段

        冲突校验规则（逐条校验，互不影响）：
        - 时间必须对齐整点，且起止至少相差 1 小时
        - 不能是过去的时段
        - 与已发布的任意时段重叠 → 跳过并记录
        - 与未完成预约的时间重叠 → 跳过并记录（该时间已有咨询安排）
        """
        counselor = ScheduleService._get_counselor_by_user(db, user_id)
        now = datetime.now()

        created, skipped, conflicts = 0, 0, []
        # 预加载已有数据，避免循环内重复查询
        existing_slots = db.query(CounselorTimeSlot).filter(
            CounselorTimeSlot.counselor_id == counselor.id,
            CounselorTimeSlot.status != 'disabled'
        ).all()
        active_appointments = db.query(Appointment).filter(
            Appointment.counselor_id == counselor.id,
            Appointment.status.in_(['pending', 'confirmed', 'in_progress'])
        ).all()

        for item in request.slots:
            label = f"{item.date} {item.start_time}-{item.end_time}"
            try:
                slot_date = datetime.strptime(item.date, "%Y-%m-%d").date()
                start = datetime.strptime(item.start_time, "%H:%M").time()
                end = datetime.strptime(item.end_time, "%H:%M").time()
            except ValueError:
                conflicts.append(f"{label}：日期或时间格式错误")
                skipped += 1
                continue

            slot_start = datetime.combine(slot_date, start)
            slot_end = datetime.combine(slot_date, end)

            if slot_end <= slot_start:
                conflicts.append(f"{label}：结束时间必须晚于开始时间")
                skipped += 1
                continue
            if item.start_time[-2:] != '00' or item.end_time[-2:] != '00':
                conflicts.append(f"{label}：时段必须对齐整点（如 09:00-12:00）")
                skipped += 1
                continue
            if (slot_end - slot_start).total_seconds() < 3600:
                conflicts.append(f"{label}：时段至少为 1 小时")
                skipped += 1
                continue
            if slot_start < now:
                conflicts.append(f"{label}：不能发布过去的时段")
                skipped += 1
                continue

            # 按整点拆分为 1 小时的子时段：每个小时独立可约、独立锁定
            # （预约时长固定 60 分钟，拆分后单条预约只占用自己那一小时）
            # 冲突校验同粒度进行：部分重叠时只跳过冲突的那一小时，其余照常发布
            hour_start = slot_start
            while hour_start < slot_end:
                hour_end = hour_start + timedelta(hours=1)
                h_start, h_end = hour_start.time(), hour_end.time()
                h_label = f"{item.date} {hour_start.strftime('%H:%M')}-{hour_end.strftime('%H:%M')}"

                # 与已发布时段重叠校验
                overlap_slot = next(
                    (s for s in existing_slots
                     if s.slot_date == slot_date
                     and s.start_time < h_end and s.end_time > h_start),
                    None
                )
                if overlap_slot is not None:
                    conflicts.append(
                        f"{h_label}：与已发布时段 "
                        f"{overlap_slot.start_time.strftime('%H:%M')}-"
                        f"{overlap_slot.end_time.strftime('%H:%M')} 重叠"
                    )
                    skipped += 1
                    hour_start = hour_end
                    continue

                # 与未完成预约重叠校验
                overlap_appt = None
                for appt in active_appointments:
                    appt_start = appt.appointment_date
                    if appt_start.tzinfo is not None:
                        appt_start = appt_start.replace(tzinfo=None)
                    if appt_start.date() != slot_date:
                        continue
                    appt_end = appt_start + timedelta(minutes=appt.duration or 60)
                    if appt_start < hour_end and appt_end > hour_start:
                        overlap_appt = appt
                        break
                if overlap_appt is not None:
                    conflicts.append(
                        f"{h_label}：与已有预约（"
                        f"{overlap_appt.appointment_date.strftime('%H:%M')} 开始）时间冲突"
                    )
                    skipped += 1
                    hour_start = hour_end
                    continue

                slot = CounselorTimeSlot(
                    counselor_id=counselor.id,
                    slot_date=slot_date,
                    start_time=h_start,
                    end_time=h_end,
                    status='available'
                )
                db.add(slot)
                existing_slots.append(slot)
                created += 1
                hour_start = hour_end

        if created > 0:
            db.commit()

        return {
            "created": created,
            "skipped": skipped,
            "conflicts": conflicts
        }

    @staticmethod
    def get_my_slots(db: Session, user_id: int, query_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询咨询师自己的排班时段（可按日期过滤，默认全部未来时段）"""
        counselor = ScheduleService._get_counselor_by_user(db, user_id)

        q = db.query(CounselorTimeSlot).filter(
            CounselorTimeSlot.counselor_id == counselor.id,
            CounselorTimeSlot.status != 'disabled'
        )
        if query_date:
            try:
                d = datetime.strptime(query_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("日期格式错误，应为 YYYY-MM-DD")
            q = q.filter(CounselorTimeSlot.slot_date == d)
        else:
            q = q.filter(CounselorTimeSlot.slot_date >= date.today())

        slots = q.order_by(CounselorTimeSlot.slot_date, CounselorTimeSlot.start_time).all()
        return [
            {
                "id": s.id,
                "slot_date": s.slot_date.strftime("%Y-%m-%d"),
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "status": s.status
            }
            for s in slots
        ]

    @staticmethod
    def remove_slot(db: Session, user_id: int, slot_id: int) -> bool:
        """删除已发布时段（已被预约的时段不可删除，需先取消对应预约）"""
        counselor = ScheduleService._get_counselor_by_user(db, user_id)

        slot = db.query(CounselorTimeSlot).filter(
            CounselorTimeSlot.id == slot_id,
            CounselorTimeSlot.counselor_id == counselor.id
        ).first()
        if not slot:
            raise ValueError("时段不存在或无权操作")
        if slot.status == 'booked':
            raise ValueError("该时段已被预约占用，无法删除；请先取消对应预约")

        db.delete(slot)
        db.commit()
        return True
