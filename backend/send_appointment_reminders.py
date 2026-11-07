"""
预约提醒定时任务脚本

功能：
- 检查未来1小时内的预约
- 发送提醒邮件给用户和咨询师
- 标记已发送提醒的预约，避免重复发送

使用方法：
1. 直接运行：python send_appointment_reminders.py
2. 定时任务（Linux crontab）：
   */10 * * * * cd /path/to/backend && python send_appointment_reminders.py
3. 定时任务（Windows Task Scheduler）：
   创建任务每10分钟运行一次此脚本
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor
from app.models.user import User
from app.services.email_service import EmailService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/appointment_reminders.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_reminder_for_appointment(db, appointment: Appointment):
    """
    为单个预约发送提醒邮件

    Args:
        db: 数据库会话
        appointment: 预约对象
    """
    try:
        # 获取用户和咨询师信息
        user = db.query(User).filter(User.id == appointment.user_id).first()
        counselor = db.query(Counselor).filter(Counselor.id == appointment.counselor_id).first()

        if not user or not counselor:
            logger.warning(f"预约 {appointment.id} 缺少用户或咨询师信息")
            return

        # 格式化预约时间
        appointment_date_str = appointment.appointment_date.strftime("%Y-%m-%d")
        appointment_time_str = appointment.appointment_date.strftime("%H:%M")

        # 发送给用户
        if user.email:
            try:
                EmailService.send_appointment_reminder(
                    email=user.email,
                    nickname=user.nickname or "用户",
                    counselor_name=counselor.name,
                    appointment_date=appointment_date_str,
                    appointment_time=appointment_time_str,
                    consultation_type=appointment.consultation_type
                )
                logger.info(f"已发送提醒邮件给用户: {user.email}, 预约ID: {appointment.id}")
            except Exception as e:
                logger.error(f"发送用户提醒邮件失败: {e}")

        # 发送给咨询师
        if counselor.email:
            try:
                EmailService.send_appointment_reminder(
                    email=counselor.email,
                    nickname=counselor.name,
                    counselor_name=counselor.name,  # 咨询师给自己发送提醒
                    appointment_date=appointment_date_str,
                    appointment_time=appointment_time_str,
                    consultation_type=appointment.consultation_type
                )
                logger.info(f"已发送提醒邮件给咨询师: {counselor.email}, 预约ID: {appointment.id}")
            except Exception as e:
                logger.error(f"发送咨询师提醒邮件失败: {e}")

        # 标记已发送提醒
        appointment.reminder_sent = True
        appointment.reminder_sent_at = datetime.now()
        db.commit()

    except Exception as e:
        logger.error(f"处理预约 {appointment.id} 时出错: {e}")
        db.rollback()


def check_and_send_reminders():
    """检查并发送预约提醒"""
    db = SessionLocal()
    try:
        # 获取当前时间和1小时后的时间
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1)

        logger.info(f"开始检查预约提醒: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        # 查询需要发送提醒的预约
        # 条件：
        # 1. 状态为 confirmed 或 in_progress
        # 2. 预约时间在接下来1小时内
        # 3. 未发送过提醒
        appointments = db.query(Appointment).filter(
            Appointment.status.in_(['confirmed', 'in_progress']),
            Appointment.appointment_date >= now,
            Appointment.appointment_date <= one_hour_later,
            Appointment.reminder_sent.is_(False)  # 假设模型中有 reminder_sent 字段
        ).all()

        logger.info(f"找到 {len(appointments)} 个需要发送提醒的预约")

        # 为每个预约发送提醒
        for appointment in appointments:
            send_reminder_for_appointment(db, appointment)

        logger.info("预约提醒检查完成")

    except Exception as e:
        logger.error(f"检查预约提醒时出错: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("预约提醒定时任务启动")
    logger.info("=" * 60)

    try:
        check_and_send_reminders()
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")

    logger.info("=" * 60)
    logger.info("预约提醒定时任务结束")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
