"""
后台管理服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, case
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.models.admin import Admin
from app.models.user import User
from app.models.counselor import Counselor, Appointment
from app.models.knowledge import KnowledgeArticle
from app.models.test import TestResult
from app.models.chat import ChatDialogue, ChatMessage, ChatTag, ChatDialogueTag
from app.schemas.admin import (
    AdminResponse, DashboardStats, ChartDataPoint, ChartResponse,
    CounselorReviewResponse, ReviewCounselorRequest,
    ArticleSaveRequest, AdminUserResponse, BanUserRequest,
    AdminOrderResponse
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminService:
    """管理员服务"""

    @staticmethod
    def authenticate_admin(db: Session, username: str, password: str) -> Optional[Admin]:
        """验证管理员登录（支持邮箱或用户名）"""
        # 先尝试用邮箱查找，再用用户名查找
        admin = db.query(Admin).filter(
            (Admin.email == username) | (Admin.username == username),
            Admin.deleted_at.is_(None)
        ).first()

        if not admin:
            return None

        if not admin.is_active:
            raise ValueError("管理员账号已被禁用")

        if not pwd_context.verify(password, admin.password_hash):
            return None

        # 更新最后登录时间
        admin.last_login_at = datetime.now()
        db.commit()

        return admin

    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        """获取仪表盘统计数据"""
        # 用户总数
        user_count = db.query(User).filter(User.is_deleted == False).count()

        # 今日新增用户
        today = datetime.now().date()
        today_user_count = db.query(User).filter(
            User.is_deleted == False,
            func.date(User.created_at) == today
        ).count()

        # 咨询师总数
        counselor_count = db.query(Counselor).filter(Counselor.is_deleted == False).count()

        # 待审核咨询师
        pending_counselor_count = db.query(Counselor).filter(
            Counselor.is_deleted == False,
            Counselor.is_verified == False
        ).count()

        # 订单总数
        order_count = db.query(Appointment).count()

        # 今日订单数
        today_order_count = db.query(Appointment).filter(
            func.date(Appointment.created_at) == today
        ).count()

        # 总收入
        total_revenue = db.query(func.sum(Appointment.paid_amount)).scalar() or 0

        # 文章总数
        article_count = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.is_deleted == False
        ).count()

        return DashboardStats(
            user_count=user_count,
            counselor_count=counselor_count,
            order_count=order_count,
            article_count=article_count,
            today_user_count=today_user_count,
            today_order_count=today_order_count,
            total_revenue=float(total_revenue),
            pending_counselor_count=pending_counselor_count
        )

    @staticmethod
    def get_chart_data(db: Session, chart_type: str) -> ChartResponse:
        """获取图表数据"""
        if chart_type == "user":
            # 用户增长趋势（最近30天）
            dates = []
            values = []
            for i in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                count = db.query(User).filter(
                    User.is_deleted == False,
                    func.date(User.created_at) == date
                ).count()
                dates.append(date.strftime("%Y-%m-%d"))
                values.append(float(count))

            return ChartResponse(
                type="user",
                data=[ChartDataPoint(date=d, value=v) for d, v in zip(dates, values)]
            )

        elif chart_type == "trend":
            # 综合活动趋势（最近7天）
            dates = []
            values = []
            for i in range(7, 0, -1):
                date = (datetime.now() - timedelta(days=i)).date()

                # 统计该日的活动数量（测试+对话+订单）
                test_count = db.query(TestResult).filter(
                    func.date(TestResult.created_at) == date
                ).count()

                chat_count = db.query(ChatDialogue).filter(
                    func.date(ChatDialogue.created_at) == date
                ).count()

                order_count = db.query(Appointment).filter(
                    func.date(Appointment.created_at) == date
                ).count()

                total = test_count + chat_count + order_count
                dates.append(date.strftime("%m-%d"))
                values.append(float(total))

            return ChartResponse(
                type="trend",
                data=[ChartDataPoint(date=d, value=v) for d, v in zip(dates, values)]
            )

        elif chart_type == "order":
            # 订单趋势（最近30天）
            dates = []
            values = []
            for i in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                count = db.query(Appointment).filter(
                    func.date(Appointment.created_at) == date
                ).count()
                dates.append(date.strftime("%m-%d"))
                values.append(float(count))

            return ChartResponse(
                type="order",
                data=[ChartDataPoint(date=d, value=v) for d, v in zip(dates, values)]
            )

        elif chart_type == "revenue":
            # 收入趋势（最近30天）
            dates = []
            values = []
            for i in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                revenue = db.query(func.sum(Appointment.paid_amount)).filter(
                    func.date(Appointment.created_at) == date
                ).scalar() or 0
                dates.append(date.strftime("%m-%d"))
                values.append(float(revenue))

            total = sum(values)
            return ChartResponse(
                type="revenue",
                data=[ChartDataPoint(date=d, value=v) for d, v in zip(dates, values)],
                total=total
            )

        else:
            raise ValueError("不支持的图表类型")

    @staticmethod
    def get_pending_counselors(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        status_filter: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取咨询师申请列表（支持状态过滤和关键词搜索）"""
        base_q = db.query(Counselor).filter(Counselor.is_deleted == False)

        # 各状态计数
        counts = {
            "pending": base_q.filter(Counselor.application_status == 'pending').count(),
            "approved": base_q.filter(Counselor.application_status == 'approved').count(),
            "rejected": base_q.filter(Counselor.application_status == 'rejected').count(),
        }

        # 过滤状态
        if status_filter and status_filter in ('pending', 'approved', 'rejected'):
            q = base_q.filter(Counselor.application_status == status_filter)
        else:
            q = base_q.filter(Counselor.application_status == 'pending')

        # 关键词搜索（姓名）
        if keyword:
            q = q.filter(Counselor.name.contains(keyword))

        q = q.order_by(Counselor.created_at.asc())

        total = q.count()
        offset = (page - 1) * page_size
        counselors = q.offset(offset).limit(page_size).all()

        items = [CounselorReviewResponse.model_validate(c) for c in counselors]

        return {
            "total": total,
            "list": items,
            "counts": counts,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def review_counselor(
        db: Session,
        counselor_id: int,
        review_data: ReviewCounselorRequest
    ) -> bool:
        """审核咨询师"""
        counselor = db.query(Counselor).filter(
            Counselor.id == counselor_id,
            Counselor.is_deleted == False
        ).first()

        if not counselor:
            raise ValueError("咨询师不存在")

        if counselor.is_verified:
            raise ValueError("咨询师已审核")

        if review_data.action == "approve":
            counselor.is_verified = True
            counselor.status = "active"

            # 发送通知给咨询师
            from app.services.notification_service import NotificationService
            NotificationService.notify_counselor_approved(db, counselor.user_id)
        elif review_data.action == "reject":
            # 拒绝后删除咨询师
            counselor.is_deleted = True
            counselor.deleted_at = datetime.now()

            # 发送通知给咨询师
            from app.services.notification_service import NotificationService
            NotificationService.notify_counselor_rejected(db, counselor.user_id, review_data.reason)
        else:
            raise ValueError("无效的审核操作")

        db.commit()
        return True

    @staticmethod
    def save_article(
        db: Session,
        article_data: ArticleSaveRequest
    ) -> int:
        """保存文章"""
        if article_data.id:
            # 更新
            article = db.query(KnowledgeArticle).filter(
                KnowledgeArticle.id == article_data.id,
                KnowledgeArticle.is_deleted == False
            ).first()

            if not article:
                raise ValueError("文章不存在")

            # 更新字段
            article.title = article_data.title
            article.summary = article_data.summary
            article.cover_image = article_data.cover_image
            article.content = article_data.content
            article.content_type = article_data.content_type
            article.category = article_data.category
            article.tags = article_data.tags
            article.status = article_data.status
            article.seo_keywords = article_data.seo_keywords
            article.seo_description = article_data.seo_description

            # 如果状态从draft变为published，设置发布时间
            if article_data.status == "published" and not article.published_at:
                article.published_at = datetime.now()

            db.commit()
            return article.id

        else:
            # 创建
            article = KnowledgeArticle(
                title=article_data.title,
                summary=article_data.summary,
                cover_image=article_data.cover_image,
                content=article_data.content,
                content_type=article_data.content_type,
                category=article_data.category,
                tags=article_data.tags,
                status=article_data.status,
                seo_keywords=article_data.seo_keywords,
                seo_description=article_data.seo_description,
                author_name="系统管理员"
            )

            # 如果是发布状态，设置发布时间
            if article_data.status == "published":
                article.published_at = datetime.now()

            db.add(article)
            db.commit()
            db.refresh(article)
            return article.id

    @staticmethod
    def delete_article(db: Session, article_id: int) -> bool:
        """删除文章"""
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.is_deleted == False
        ).first()

        if not article:
            raise ValueError("文章不存在")

        article.is_deleted = True
        db.commit()

        return True

    @staticmethod
    def get_users(
        db: Session,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取用户列表（返回前端 camelCase 格式）"""
        from app.models.knowledge import KnowledgeFavorite

        q = db.query(User).filter(User.is_deleted == False)

        # 关键词搜索
        if keyword:
            q = q.filter(
                User.email.contains(keyword) |
                User.nickname.contains(keyword) |
                User.phone.contains(keyword)
            )

        # 按创建时间倒序
        q = q.order_by(desc(User.created_at))

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        users = q.offset(offset).limit(page_size).all()

        def fmt_dt(dt):
            return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

        def fmt_date(d):
            return d.strftime('%Y-%m-%d') if d else None

        # 转换为前端期望的 camelCase 格式
        items = []
        for user in users:
            test_count = db.query(TestResult).filter(
                TestResult.user_id == user.id
            ).count()

            chat_count = db.query(ChatDialogue).filter(
                ChatDialogue.user_id == user.id
            ).count()

            order_count = db.query(Appointment).filter(
                Appointment.user_id == user.id
            ).count()

            favorite_count = db.query(KnowledgeFavorite).filter(
                KnowledgeFavorite.user_id == user.id
            ).count()

            items.append({
                "id": user.id,
                "email": user.email,
                "username": user.email,          # 用邮箱充当用户名
                "nickname": user.nickname,
                "avatar": user.avatar,
                "phone": user.phone,
                "role": user.role or "user",
                "gender": user.gender,
                "birthDate": fmt_date(user.birth_date),
                "bio": None,
                "banned": user.status == "banned",
                "status": user.status or "active",
                "is_verified": user.is_verified,
                "lastLoginTime": fmt_dt(user.last_login_at),
                "createdAt": fmt_dt(user.created_at),
                "testCount": test_count,
                "chatCount": chat_count,
                "appointmentCount": order_count,
                "favoriteCount": favorite_count,
            })

        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size
        }

    @staticmethod
    def ban_user(db: Session, user_id: int, ban_data: BanUserRequest) -> bool:
        """封禁/解封用户"""
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not user:
            raise ValueError("用户不存在")

        if ban_data.banned:
            user.status = "banned"
        else:
            user.status = "active"

        db.commit()
        return True

    @staticmethod
    def get_orders(
        db: Session,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取订单列表"""
        q = db.query(Appointment)

        # 状态筛选
        if status_filter:
            q = q.filter(Appointment.status == status_filter)

        # 按创建时间倒序
        q = q.order_by(desc(Appointment.created_at))

        # 总数
        total = q.count()

        # 分页
        offset = (page - 1) * page_size
        orders = q.offset(offset).limit(page_size).all()

        # 转换为响应格式
        items = []
        for order in orders:
            order_data = AdminOrderResponse.model_validate(order)

            # 添加用户和咨询师信息
            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                order_data.user_name = order_data.user_name or user.nickname

            counselor = db.query(Counselor).filter(Counselor.id == order.counselor_id).first()
            if counselor:
                order_data.counselor_name = counselor.name

            items.append(order_data)

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def export_orders(db: Session) -> bytes:
        """导出订单数据为CSV"""
        import csv
        from io import StringIO

        # 获取所有订单
        orders = db.query(Appointment).order_by(desc(Appointment.created_at)).all()

        # 创建CSV
        output = StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow([
            "预约编号", "用户ID", "用户姓名", "联系方式",
            "咨询师ID", "咨询师姓名", "咨询方式",
            "预约时间", "价格", "已付金额", "状态",
            "创建时间", "完成时间", "取消时间"
        ])

        # 写入数据
        for order in orders:
            # 获取用户和咨询师信息
            user = db.query(User).filter(User.id == order.user_id).first()
            user_name = order.user_name or (user.nickname if user else "")

            counselor = db.query(Counselor).filter(Counselor.id == order.counselor_id).first()
            counselor_name = counselor.name if counselor else ""

            writer.writerow([
                order.appointment_no,
                order.user_id,
                user_name,
                order.user_contact or "",
                order.counselor_id,
                counselor_name,
                order.consultation_type,
                order.appointment_date.strftime("%Y-%m-%d %H:%M:%S") if order.appointment_date else "",
                order.price,
                order.paid_amount,
                order.status,
                order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
                order.completed_at.strftime("%Y-%m-%d %H:%M:%S") if order.completed_at else "",
                order.cancelled_at.strftime("%Y-%m-%d %H:%M:%S") if order.cancelled_at else ""
            ])

        # 返回字节数据
        output.seek(0)
        return output.read().encode('utf-8-sig')

    # ==================== 对话管理 ====================

    @staticmethod
    def get_dialogues(
        db: Session,
        user_id: Optional[int] = None,
        tag_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取所有对话列表（管理员视角）"""
        q = db.query(ChatDialogue).filter(
            ChatDialogue.is_deleted == False
        )

        # 按用户筛选
        if user_id:
            q = q.filter(ChatDialogue.user_id == user_id)

        # 按标签筛选
        if tag_name:
            q = q.join(ChatDialogue.tags).join(ChatDialogueTag.tag).filter(
                and_(
                    ChatTag.name == tag_name,
                    ChatTag.is_deleted == False
                )
            ).distinct()

        q = q.order_by(desc(ChatDialogue.updated_at))

        total = q.count()
        offset = (page - 1) * page_size
        dialogues = q.offset(offset).limit(page_size).all()

        items = []
        for dialogue in dialogues:
            user = db.query(User).filter(User.id == dialogue.user_id).first()

            msg_count = db.query(func.count(ChatMessage.id)).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).scalar() or 0

            last_msg = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.dialogue_id == dialogue.id,
                    ChatMessage.is_deleted == False
                )
            ).order_by(desc(ChatMessage.created_at)).first()

            tags = db.query(ChatTag).join(
                ChatDialogueTag, ChatDialogueTag.tag_id == ChatTag.id
            ).filter(
                ChatDialogueTag.dialogue_id == dialogue.id
            ).all()

            items.append({
                "id": dialogue.id,
                "user_id": dialogue.user_id,
                "user_name": user.nickname if user else f"用户{dialogue.user_id}",
                "user_avatar": user.avatar if user else None,
                "title": dialogue.title,
                "message_count": msg_count,
                "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
                "last_message": last_msg.content[:80] if last_msg else None,
                "last_message_role": last_msg.role if last_msg else None,
                "created_at": dialogue.created_at,
                "updated_at": dialogue.updated_at
            })

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_dialogue_detail(db: Session, dialogue_id: int) -> Optional[Dict[str, Any]]:
        """获取对话详情（管理员视角）"""
        dialogue = db.query(ChatDialogue).filter(
            and_(
                ChatDialogue.id == dialogue_id,
                ChatDialogue.is_deleted == False
            )
        ).first()

        if not dialogue:
            return None

        user = db.query(User).filter(User.id == dialogue.user_id).first()

        messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.dialogue_id == dialogue_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(ChatMessage.created_at).all()

        tags = db.query(ChatTag).join(
            ChatDialogueTag, ChatDialogueTag.tag_id == ChatTag.id
        ).filter(
            ChatDialogueTag.dialogue_id == dialogue_id
        ).all()

        return {
            "id": dialogue.id,
            "user_id": dialogue.user_id,
            "user_name": user.nickname if user else f"用户{dialogue.user_id}",
            "user_avatar": user.avatar if user else None,
            "title": dialogue.title,
            "created_at": dialogue.created_at,
            "updated_at": dialogue.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags]
        }
