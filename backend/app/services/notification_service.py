"""通知服务层"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, Dict, Any

from app.models.notification import Notification


class NotificationService:
    """通知服务"""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        type: str,
        title: str,
        content: str,
        related_id: Optional[int] = None
    ) -> Notification:
        """创建通知"""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            related_id=related_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """获取未读通知数"""
        return db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).scalar() or 0

    @staticmethod
    def get_list(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取通知列表"""
        q = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(desc(Notification.created_at))

        total = q.count()
        offset = (page - 1) * page_size
        items = q.offset(offset).limit(page_size).all()

        unread_count = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).scalar() or 0

        return {
            "total": total,
            "items": items,
            "unread_count": unread_count,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def mark_read(db: Session, notification_id: int, user_id: int) -> bool:
        """标记单条通知为已读"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if not notification:
            return False
        notification.is_read = True
        db.commit()
        return True

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        """标记所有通知为已读，返回更新的数量"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count

    # ========== 业务事件触发器 ==========

    @staticmethod
    def notify_appointment_confirmed(db: Session, user_id: int, appointment_id: int, counselor_name: str = "", appointment_date: str = ""):
        """咨询师确认预约"""
        NotificationService.create(
            db, user_id, "appointment_confirmed",
            "预约状态更新",
            "您的预约已被确认",
            appointment_id
        )

    @staticmethod
    def notify_appointment_rejected(db: Session, user_id: int, appointment_id: int, counselor_name: str = "", reason: str = ""):
        """咨询师拒绝预约"""
        NotificationService.create(
            db, user_id, "appointment_rejected",
            "预约状态更新",
            "您的预约已被拒绝",
            appointment_id
        )

    @staticmethod
    def notify_counselor_approved(db: Session, counselor_user_id: int):
        """咨询师入驻申请通过"""
        NotificationService.create(
            db, counselor_user_id, "counselor_approved",
            "入驻申请已通过",
            "恭喜！您的咨询师入驻申请已审核通过，现在可以开始接单了。"
        )

    @staticmethod
    def notify_counselor_rejected(db: Session, counselor_user_id: int, reason: str = ""):
        """咨询师入驻申请被拒"""
        extra = f"：{reason}" if reason else ""
        NotificationService.create(
            db, counselor_user_id, "counselor_rejected",
            "入驻申请未通过",
            f"很遗憾，您的咨询师入驻申请未通过审核{extra}"
        )

    @staticmethod
    def notify_new_counselor_application(db: Session, admin_user_id: int, counselor_name: str = ""):
        """通知管理员有新的咨询师申请"""
        NotificationService.create(
            db, admin_user_id, "new_counselor_application",
            "新的入驻申请",
            "有咨询师提交了入驻申请，请尽快审核。"
        )

    @staticmethod
    def notify_system(db: Session, user_id: int, title: str, content: str):
        """系统通知"""
        NotificationService.create(db, user_id, "system", title, content)

    @staticmethod
    def notify_new_appointment(db: Session, counselor_user_id: int, appointment_id: int, user_name: str = "", appointment_date: str = ""):
        """用户预约 → 通知咨询师"""
        NotificationService.create(
            db, counselor_user_id, "new_appointment",
            "新的咨询预约",
            "您有一条新的咨询预约，请及时处理。",
            appointment_id
        )

    @staticmethod
    def notify_appointment_cancelled(db: Session, user_id: int, appointment_id: int, by_user_name: str = ""):
        """预约被取消 → 通知对方"""
        NotificationService.create(
            db, user_id, "appointment_cancelled",
            "预约状态更新",
            "有一条预约已被取消",
            appointment_id
        )

    @staticmethod
    def notify_appointment_completed(db: Session, user_id: int, appointment_id: int, counselor_name: str = ""):
        """咨询完成 → 通知用户"""
        NotificationService.create(
            db, user_id, "appointment_completed",
            "咨询已完成",
            "有一条咨询已结束",
            appointment_id
        )

    @staticmethod
    def notify_new_message(db: Session, receiver_user_id: int, appointment_id: int, sender_name: str = "", message_preview: str = ""):
        """新消息 → 通知对方"""
        NotificationService.create(
            db, receiver_user_id, "new_message",
            "收到一条新消息",
            "您收到一条新消息",
            appointment_id
        )


# 全局实例
notification_service = NotificationService()
