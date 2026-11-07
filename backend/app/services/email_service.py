"""
邮件服务
"""
import smtplib
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""

    # SMTP 默认超时（秒）
    SMTP_TIMEOUT = 30
    # 最大重试次数
    MAX_RETRIES = 2
    # IP 直连回退（绕过 DNS 解析）
    SMTP_IPS = {
        "smtp.163.com": ["111.124.203.45", "111.124.203.55"],
    }

    @staticmethod
    def _resolve_smtp_host() -> str:
        """尝试解析 SMTP 服务器 IP，必要时直接返回 IP 直连"""
        host = settings.MAIL_SERVER
        if host not in EmailService.SMTP_IPS:
            return host
        # 尝试 DNS 解析
        try:
            socket.getaddrinfo(host, settings.MAIL_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
            return host  # DNS 正常，使用域名
        except socket.gaierror:
            logger.warning(f"DNS 解析失败，尝试 IP 直连 {host}")
            return EmailService.SMTP_IPS[host][0]

    @staticmethod
    def _create_connection(host: str, timeout: int):
        """创建带超时的 SMTP/SSL 连接"""
        if settings.MAIL_TLS:
            server = smtplib.SMTP(host, settings.MAIL_PORT, timeout=timeout)
            server.starttls()
        elif settings.MAIL_SSL:
            server = smtplib.SMTP_SSL(host, settings.MAIL_PORT, timeout=timeout)
        else:
            server = smtplib.SMTP(host, settings.MAIL_PORT, timeout=timeout)
        return server

    @staticmethod
    def create_smtp_connection():
        """创建SMTP连接（带超时 + IP直连回退）"""
        host = EmailService._resolve_smtp_host()
        last_error = None

        for attempt in range(1, EmailService.MAX_RETRIES + 2):  # 最多 3 次
            try:
                logger.info(f"SMTP 连接尝试 {attempt}: {host}:{settings.MAIL_PORT}")
                server = EmailService._create_connection(host, EmailService.SMTP_TIMEOUT)
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                logger.info(f"SMTP 登录成功 ({host})")
                return server
            except (socket.gaierror, socket.timeout) as e:
                last_error = e
                logger.warning(f"SMTP 连接失败 (尝试 {attempt}): {e}")
                # DNS 失败时尝试 IP 直连
                if isinstance(e, socket.gaierror) and host == settings.MAIL_SERVER:
                    ips = EmailService.SMTP_IPS.get(host)
                    if ips and len(ips) > 0:
                        host = ips[min(attempt - 1, len(ips) - 1)]
                        logger.info(f"切换到 IP 直连: {host}")
                    else:
                        host = settings.MAIL_SERVER
                if attempt <= EmailService.MAX_RETRIES:
                    time.sleep(attempt * 2)  # 指数退避
            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP 认证失败，请检查邮箱账号和授权码")
                raise
            except Exception as e:
                last_error = e
                logger.error(f"创建SMTP连接失败 (尝试 {attempt}): {e}")
                if attempt <= EmailService.MAX_RETRIES:
                    time.sleep(attempt * 2)

        logger.error(f"所有 SMTP 连接尝试均失败")
        raise last_error or Exception("无法连接到SMTP服务器")

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: 邮件内容（HTML格式）

        Returns:
            bool: 是否发送成功
        """
        try:
            logger.info(f"准备发送邮件到: {to_email}")

            # 清理邮箱地址
            to_email = to_email.strip().lower()
            if not to_email:
                raise ValueError("收件人邮箱地址为空")

            # 创建邮件对象
            message = MIMEMultipart("alternative")
            message["Subject"] = Header(subject, 'utf-8').encode()
            # QQ邮箱要求From头部必须严格按照RFC5322标准
            # 方案1: 只使用邮箱地址（最简单可靠）
            message["From"] = settings.MAIL_FROM
            # 方案2: 如果需要显示名称，使用以下格式
            # message["From"] = formataddr((Header(settings.MAIL_FROM_NAME, 'utf-8').encode(), settings.MAIL_FROM))
            message["To"] = to_email

            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            logger.info(f"邮件内容准备完成，准备连接SMTP服务器")
            logger.info(f"发件人: {settings.MAIL_FROM}")
            logger.info(f"收件人: {to_email}")

            # 发送邮件
            with EmailService.create_smtp_connection() as server:
                server.sendmail(settings.MAIL_FROM, to_email, message.as_string())

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise

    @staticmethod
    def send_verification_code(email: str, code: str) -> bool:
        """
        发送验证码邮件

        Args:
            email: 收件人邮箱
            code: 验证码

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】邮箱验证码"

        # 邮件HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    text-align: center;
                    padding: 20px;
                    background-color: #f0f0f0;
                    border-radius: 8px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
                .warning {{
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 15px;
                    padding: 10px;
                    background-color: #fee;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>邮箱验证码</h2>
                    <p>您好！</p>
                    <p>您正在进行邮箱验证，验证码如下：</p>
                    <div class="code">{code}</div>
                    <p><strong>有效期：5分钟</strong></p>
                    <div class="warning">
                        ⚠️ 请勿将验证码告知他人，以确保您的账户安全。
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_welcome_email(email: str, nickname: str) -> bool:
        """
        发送欢迎邮件

        Args:
            email: 收件人邮箱
            nickname: 用户昵称

        Returns:
            bool: 是否发送成功
        """
        subject = "欢迎加入 SoulStation 心理咨询平台"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation</div>
                </div>
                <div class="content">
                    <h2>欢迎加入！</h2>
                    <p>亲爱的 <strong>{nickname}</strong>：</p>
                    <p>欢迎您注册 SoulStation 心理咨询平台！</p>
                    <p>我们致力于为您提供专业的心理咨询服务，帮助您解决心理困扰，提升心理健康水平。</p>
                    <p>在平台上，您可以：</p>
                    <ul>
                        <li>进行专业心理测试</li>
                        <li>💬 与智能AI助手对话</li>
                        <li>👨‍⚕️ 预约专业咨询师</li>
                        <li>📚 阅读心理知识文章</li>
                    </ul>
                    <div style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}" class="button">立即开始</a>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_appointment_confirmation_user(
        email: str,
        nickname: str,
        counselor_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str,
        appointment_no: str
    ) -> bool:
        """
        发送预约成功通知邮件（用户）

        Args:
            email: 用户邮箱
            nickname: 用户昵称
            counselor_name: 咨询师姓名
            appointment_date: 预约日期
            appointment_time: 预约时间
            consultation_type: 咨询方式
            appointment_no: 预约编号

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】预约成功通知"

        # 咨询方式中文映射
        type_map = {
            'video': '视频咨询',
            'voice': '语音咨询',
            'offline': '线下咨询'
        }
        consultation_type_cn = type_map.get(consultation_type, consultation_type)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .info-box {{
                    background-color: #f0f7ff;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .info-item {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #667eea;
                    display: inline-block;
                    width: 100px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
                .tip {{
                    background-color: #fff3cd;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                    border-left: 4px solid #ffc107;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>🎉 预约成功</h2>
                    <p>亲爱的 <strong>{nickname}</strong>：</p>
                    <p>您已成功预约咨询服务，详细信息如下：</p>

                    <div class="info-box">
                        <div class="info-item">
                            <span class="info-label">预约编号：</span>
                            {appointment_no}
                        </div>
                        <div class="info-item">
                            <span class="info-label">咨询师：</span>
                            {counselor_name}
                        </div>
                        <div class="info-item">
                            <span class="info-label">咨询方式：</span>
                            {consultation_type_cn}
                        </div>
                        <div class="info-item">
                            <span class="info-label">预约日期：</span>
                            {appointment_date}
                        </div>
                        <div class="info-item">
                            <span class="info-label">预约时间：</span>
                            {appointment_time}
                        </div>
                    </div>

                    <div class="tip">
                        💡 <strong>温馨提示：</strong>
                        <ul style="margin: 10px 0 0 20px;">
                            <li>请提前5-10分钟准备好咨询设备</li>
                            <li>如需改期或取消，请至少提前24小时操作</li>
                            <li>咨询开始前会收到提醒通知</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_appointment_confirmation_counselor(
        email: str,
        counselor_name: str,
        user_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str,
        appointment_no: str,
        problem_description: str = ""
    ) -> bool:
        """
        发送预约成功通知邮件（咨询师）

        Args:
            email: 咨询师邮箱
            counselor_name: 咨询师姓名
            user_name: 用户姓名
            appointment_date: 预约日期
            appointment_time: 预约时间
            consultation_type: 咨询方式
            appointment_no: 预约编号
            problem_description: 问题描述

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】新的预约通知"

        type_map = {
            'video': '视频咨询',
            'voice': '语音咨询',
            'offline': '线下咨询'
        }
        consultation_type_cn = type_map.get(consultation_type, consultation_type)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .info-box {{
                    background-color: #f0f7ff;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .info-item {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #667eea;
                    display: inline-block;
                    width: 100px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
                .problem-desc {{
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>📋 新的预约</h2>
                    <p>尊敬的 <strong>{counselor_name}</strong> 老师：</p>
                    <p>您收到了一个新的预约请求：</p>

                    <div class="info-box">
                        <div class="info-item">
                            <span class="info-label">预约编号：</span>
                            {appointment_no}
                        </div>
                        <div class="info-item">
                            <span class="info-label">来访者：</span>
                            {user_name}
                        </div>
                        <div class="info-item">
                            <span class="info-label">咨询方式：</span>
                            {consultation_type_cn}
                        </div>
                        <div class="info-item">
                            <span class="info-label">预约日期：</span>
                            {appointment_date}
                        </div>
                        <div class="info-item">
                            <span class="info-label">预约时间：</span>
                            {appointment_time}
                        </div>
                    </div>

                    {f'''<div class="problem-desc">
                        <strong>问题描述：</strong><br>
                        {problem_description}
                    </div>''' if problem_description else ''}

                    <p style="margin-top: 20px;">
                        请登录平台确认该预约，并提前做好咨询准备。
                    </p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_appointment_reminder(
        email: str,
        nickname: str,
        counselor_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str
    ) -> bool:
        """
        发送临近咨询提醒邮件

        Args:
            email: 收件人邮箱
            nickname: 收件人昵称
            counselor_name: 咨询师姓名
            appointment_date: 预约日期
            appointment_time: 预约时间
            consultation_type: 咨询方式

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】咨询即将开始提醒"

        type_map = {
            'video': '视频咨询',
            'voice': '语音咨询',
            'offline': '线下咨询'
        }
        consultation_type_cn = type_map.get(consultation_type, consultation_type)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .reminder-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .reminder-time {{
                    font-size: 32px;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .info-item {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #667eea;
                    display: inline-block;
                    width: 100px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>⏰ 温馨提醒</h2>
                    <p>亲爱的 <strong>{nickname}</strong>：</p>

                    <div class="reminder-box">
                        <div>您的咨询将于 <strong>1小时后</strong> 开始</div>
                        <div class="reminder-time">{appointment_date} {appointment_time}</div>
                    </div>

                    <div>
                        <div class="info-item">
                            <span class="info-label">咨询师：</span>
                            {counselor_name}
                        </div>
                        <div class="info-item">
                            <span class="info-label">咨询方式：</span>
                            {consultation_type_cn}
                        </div>
                    </div>

                    <p style="margin-top: 20px;">
                        请您做好准备，准时参加咨询。祝您咨询愉快！
                    </p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_appointment_cancelled(
        email: str,
        nickname: str,
        appointment_date: str,
        appointment_time: str,
        reason: str = ""
    ) -> bool:
        """
        发送预约取消通知邮件

        Args:
            email: 收件人邮箱
            nickname: 收件人昵称
            appointment_date: 预约日期
            appointment_time: 预约时间
            reason: 取消原因

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】预约已取消"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .cancel-info {{
                    background-color: #f8d7da;
                    border-left: 4px solid #dc3545;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>❌ 预约已取消</h2>
                    <p>亲爱的 <strong>{nickname}</strong>：</p>

                    <div class="cancel-info">
                        <p>您的预约已被取消：</p>
                        <p style="font-size: 18px; margin: 10px 0;">
                            <strong>{appointment_date} {appointment_time}</strong>
                        </p>
                        {f'''<p style="margin-top: 10px;"><strong>取消原因：</strong>{reason}</p>''' if reason else ''}
                    </div>

                    <p>如有需要，您可以重新预约咨询师。</p>
                    <p>感谢您的理解与支持！</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_counselor_approval(
        email: str,
        name: str
    ) -> bool:
        """
        发送咨询师审核通过通知邮件

        Args:
            email: 咨询师邮箱
            name: 咨询师姓名

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】恭喜！您的咨询师申请已通过"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .success-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .success-icon {{
                    font-size: 48px;
                    margin-bottom: 15px;
                }}
                .next-steps {{
                    background-color: #f0f7ff;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .next-steps h3 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                .next-steps ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <div class="success-box">
                        <div class="success-icon">✅</div>
                        <h2>恭喜！申请已通过</h2>
                        <p style="font-size: 18px;">亲爱的 <strong>{name}</strong> 老师</p>
                    </div>

                    <p>我们很高兴地通知您，您的咨询师申请已通过审核！</p>
                    <p>您现在可以正式开始提供咨询服务了。</p>

                    <div class="next-steps">
                        <h3>📝 接下来您可以：</h3>
                        <ul>
                            <li>登录平台完善个人信息</li>
                            <li>设置可预约时间</li>
                            <li>开始接受用户预约</li>
                            <li>与来访者进行线上咨询</li>
                        </ul>
                    </div>

                    <p style="margin-top: 20px;">
                        感谢您加入 SoulStation，期待与您一起为更多人提供专业的心理咨询服务！
                    </p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_counselor_rejection(
        email: str,
        name: str,
        reason: str = ""
    ) -> bool:
        """
        发送咨询师审核拒绝通知邮件

        Args:
            email: 咨询师邮箱
            name: 咨询师姓名
            reason: 拒绝原因

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】很遗憾，您的咨询师申请未通过审核"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .reject-box {{
                    background-color: #f8d7da;
                    border-left: 4px solid #dc3545;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .reason-box {{
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>❌ 申请未通过审核</h2>
                    <p>尊敬的 <strong>{name}</strong>：</p>

                    <div class="reject-box">
                        <p>很遗憾地通知您，您的咨询师申请未通过本次审核。</p>
                    </div>

                    {f'''<div class="reason-box">
                        <strong>未通过原因：</strong>
                        <p style="margin: 10px 0;">{reason}</p>
                    </div>''' if reason else ''}

                    <p style="margin-top: 20px;">
                        您可以根据审核意见修改资料后重新提交申请。我们期待您的再次申请！
                    </p>

                    <p style="margin-top: 15px;">
                        如有疑问，请联系客服。
                    </p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)
