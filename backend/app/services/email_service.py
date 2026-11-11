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


class EmailTemplate:
    """心屿 Mindisle 统一邮件模板

    所有对外邮件共用一套版式与品牌视觉，避免各方法里各写一份 HTML
    导致品牌名、配色不一致。配色取自心屿设计系统：
    主色 #2E6E68、深色 #22524E、渐变起点 #357B74、暖黄点缀 #F6D08A、米色底 #F6F5F1
    """

    BRAND_NAME = "心屿"
    BRAND_EN = "Mindisle"
    BRAND_TAG = "心理健康 · 陪伴平台"
    SLOGAN = "让每一种情绪，都有处可栖。"
    YEAR = "2026"

    @classmethod
    def wrap(cls, title: str, body_html: str, preheader: str = "") -> str:
        """把正文包进统一的品牌外壳

        Args:
            title: 邮件内的大标题
            body_html: 正文 HTML 片段
            preheader: 收件箱预览文字（不显示在正文里）
        """
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    body {{
        margin: 0; padding: 0;
        background-color: #F6F5F1;
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
                     "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
        line-height: 1.75;
        color: #1B2A2C;
        -webkit-font-smoothing: antialiased;
    }}
    .preheader {{ display: none !important; visibility: hidden; opacity: 0;
                  color: transparent; height: 0; width: 0; overflow: hidden; }}
    * {{ box-sizing: border-box; }}
    .outer {{ width: 100%; background-color: #F6F5F1; padding: 36px 16px; }}
    .card {{
        width: 100%; max-width: 560px; margin: 0 auto;
        background: #FFFFFF;
        border: 1px solid #E7E5DE;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 18px 44px -30px rgba(27, 42, 44, .35);
    }}
    /* 顶部品牌条：深青绿渐变，与前端主按钮一致 */
    .band {{
        background: linear-gradient(160deg, #357B74, #22524E);
        padding: 26px 30px;
    }}
    .brand-row {{ display: table; width: 100%; }}
    .brand-mark {{
        display: table-cell; width: 42px; vertical-align: middle;
    }}
    .brand-mark-inner {{
        width: 38px; height: 38px; border-radius: 12px;
        background: rgba(255, 255, 255, .16);
        border: 1px solid rgba(255, 255, 255, .28);
        text-align: center; line-height: 38px;
        font-size: 18px; color: #F6D08A;
    }}
    .brand-text {{ display: table-cell; vertical-align: middle; padding-left: 13px; }}
    .brand-name {{
        font-size: 17px; font-weight: 600; color: #FFFFFF;
        letter-spacing: .16em; line-height: 1.3;
    }}
    .brand-en {{
        font-size: 11px; color: rgba(255, 255, 255, .62);
        letter-spacing: .18em; font-style: italic; margin-top: 2px;
    }}
    .brand-tag {{
        font-size: 11px; color: rgba(255, 255, 255, .55);
        letter-spacing: .12em; margin-top: 6px;
    }}
    .content {{ padding: 30px; }}
    .content h2 {{
        margin: 0 0 18px; font-size: 18px; font-weight: 500;
        color: #1B2A2C; letter-spacing: .02em;
    }}
    .content p {{ margin: 0 0 13px; font-size: 14px; color: #3C4E51; }}
    .content strong {{ color: #1B2A2C; font-weight: 600; }}
    .muted {{ color: #7A8A8C; font-size: 13px; }}
    /* 关键数字/验证码 */
    .code {{
        margin: 22px 0; padding: 20px;
        background: #F6F5F1;
        border: 1px dashed #CFDCD9;
        border-radius: 12px;
        text-align: center;
        font-size: 34px; font-weight: 600;
        letter-spacing: 9px; color: #22524E;
        font-family: "SF Mono", Menlo, Consolas, monospace;
    }}
    /* 信息明细行 */
    .info {{
        margin: 18px 0; padding: 16px 18px;
        background: #FAF9F6;
        border: 1px solid #EDEBE4;
        border-radius: 12px;
    }}
    .info-row {{ font-size: 13.5px; color: #3C4E51; padding: 5px 0; }}
    .info-row .k {{ color: #7A8A8C; display: inline-block; min-width: 76px; }}
    .info-row .v {{ color: #1B2A2C; font-weight: 500; }}
    /* 提示条 */
    .tip {{
        margin-top: 16px; padding: 12px 15px;
        background: #EAF3F1;
        border-left: 3px solid #2E6E68;
        border-radius: 8px;
        font-size: 13px; color: #22524E;
    }}
    .tip-warn {{
        margin-top: 16px; padding: 12px 15px;
        background: #FDF6EC;
        border-left: 3px solid #C79A4E;
        border-radius: 8px;
        font-size: 13px; color: #7A5A21;
    }}
    .divider {{ height: 1px; background: #EDEBE4; margin: 22px 0; }}
    .footer {{
        padding: 20px 30px 26px;
        background: #FAF9F6;
        border-top: 1px solid #EDEBE4;
        text-align: center;
    }}
    .footer p {{ margin: 0 0 6px; font-size: 11.5px; color: #93A3A5; line-height: 1.7; }}
    .footer .slogan {{ color: #7A8A8C; font-size: 12px; margin-bottom: 10px; }}
    @media only screen and (max-width: 480px) {{
        .outer {{ padding: 20px 10px; }}
        .band {{ padding: 20px 20px; }}
        .content {{ padding: 22px 20px; }}
        .footer {{ padding: 16px 20px 20px; }}
        .code {{ font-size: 28px; letter-spacing: 6px; }}
    }}
</style>
</head>
<body>
<div class="preheader">{preheader}</div>
<div class="outer">
  <div class="card">
    <div class="band">
      <div class="brand-row">
        <div class="brand-mark"><div class="brand-mark-inner">屿</div></div>
        <div class="brand-text">
          <div class="brand-name">{cls.BRAND_NAME} {cls.BRAND_EN}</div>
          <div class="brand-en">{cls.BRAND_TAG}</div>
        </div>
      </div>
      <div class="brand-tag">{cls.SLOGAN}</div>
    </div>
    <div class="content">
      <h2>{title}</h2>
      {body_html}
    </div>
    <div class="footer">
      <p class="slogan">{cls.SLOGAN}</p>
      <p>此邮件由系统自动发送，请勿直接回复</p>
      <p>© {cls.YEAR} {cls.BRAND_NAME} {cls.BRAND_EN} · 公益心理健康支持</p>
    </div>
  </div>
</div>
</body>
</html>"""


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
            # 发件人带显示名，收件箱里显示为「心屿 Mindisle <xxx@163.com>」
            # formataddr 会对非 ASCII 名称自动做 RFC2047 编码，避免中文乱码或发信被拒
            message["From"] = formataddr(
                (str(Header(settings.MAIL_FROM_NAME, 'utf-8')), settings.MAIL_FROM)
            )
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
        """发送验证码邮件（心屿统一模板）"""
        subject = f"【{EmailTemplate.BRAND_NAME}】邮箱验证码"

        body = f"""
      <p>您好！</p>
      <p>你正在注册 {EmailTemplate.BRAND_NAME} {EmailTemplate.BRAND_EN}，验证码如下：</p>
      <div class="code">{code}</div>
      <p class="muted">验证码 5 分钟内有效，请尽快填写。</p>
      <div class="tip">如果这不是你本人的操作，忽略本邮件即可，你的账户不会有任何变化。</div>
      <div class="tip-warn">请勿将验证码告知他人，{EmailTemplate.BRAND_NAME} 的工作人员不会向你索取验证码。</div>
"""
        html_content = EmailTemplate.wrap(
            title="邮箱验证码",
            body_html=body,
            preheader=f"你的 {EmailTemplate.BRAND_NAME} 验证码是 {code}，5 分钟内有效。",
        )

        return EmailService.send_email(email, subject, html_content)

    def send_welcome_email(email: str, nickname: str) -> bool:
        """欢迎邮件：注册成功后发送"""
        subject = f"欢迎来到{EmailTemplate.BRAND_NAME} {EmailTemplate.BRAND_EN}"

        body = f"""
      <p>{nickname}，你好：</p>
      <p>很高兴你来到这里。{EmailTemplate.SLOGAN}</p>
      <p>在{EmailTemplate.BRAND_NAME}，你可以：</p>
      <div class="info">
        <div class="info-row"><span class="k">心理测评</span><span class="v">用几份温和的量表，看清自己此刻的状态</span></div>
        <div class="info-row"><span class="k">屿灯</span><span class="v">随时可以说话的地方，一个 AI 陪伴者</span></div>
        <div class="info-row"><span class="k">咨询预约</span><span class="v">预约公益心理咨询，全部免费</span></div>
      </div>
      <p class="muted">你不必先整理好自己才来到这里——慢慢来，我们等你。</p>
      <div class="tip">所有服务完全免费，你的测评与对话内容默认仅你自己可见，可随时在「隐私设置」中调整。</div>
"""
        html_content = EmailTemplate.wrap(
            title=f"欢迎来到{EmailTemplate.BRAND_NAME}",
            body_html=body,
            preheader=f"{nickname}，很高兴你来到这里。{EmailTemplate.SLOGAN}",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_appointment_confirmation_user(
        email: str,
        nickname: str,
        counselor_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str,
        appointment_no: str,
    ) -> bool:
        """预约成功通知：发给你（来访者）"""
        subject = f"【{EmailTemplate.BRAND_NAME}】预约成功通知"

        type_map = {"video": "在线咨询", "voice": "在线咨询", "offline": "线下咨询"}
        type_text = type_map.get(consultation_type, "在线咨询")

        body = f"""
      <p>{nickname}，你好：</p>
      <p>你的咨询预约已提交成功，以下是详细信息：</p>
      <div class="info">
        <div class="info-row"><span class="k">咨询师</span><span class="v">{counselor_name}</span></div>
        <div class="info-row"><span class="k">日期</span><span class="v">{appointment_date}</span></div>
        <div class="info-row"><span class="k">时间</span><span class="v">{appointment_time}</span></div>
        <div class="info-row"><span class="k">方式</span><span class="v">{type_text} · 50 分钟</span></div>
        <div class="info-row"><span class="k">费用</span><span class="v">公益免费</span></div>
        <div class="info-row"><span class="k">预约编号</span><span class="v">{appointment_no}</span></div>
      </div>
      <div class="tip">咨询师确认后，你会在「我的预约」里看到状态更新。开始前 15 分钟系统会再提醒你一次。</div>
      <p class="muted">如果时间不合适，可随时在「我的预约」中取消，不收取任何费用。</p>
"""
        html_content = EmailTemplate.wrap(
            title="预约成功",
            body_html=body,
            preheader=f"你与 {counselor_name} 的咨询已预约成功：{appointment_date} {appointment_time}",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_appointment_confirmation_counselor(
        email: str,
        counselor_name: str,
        user_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str,
        appointment_no: str,
        problem_description: str = "",
    ) -> bool:
        """新预约通知：发给咨询师"""
        subject = f"【{EmailTemplate.BRAND_NAME}】新的预约通知"

        type_map = {"video": "在线咨询", "voice": "在线咨询", "offline": "线下咨询"}
        type_text = type_map.get(consultation_type, "在线咨询")
        problem = problem_description.strip() if problem_description else "来访者未填写诉求描述"

        body = f"""
      <p>{counselor_name}老师，你好：</p>
      <p>有一位来访者预约了你的咨询：</p>
      <div class="info">
        <div class="info-row"><span class="k">来访者</span><span class="v">{user_name}</span></div>
        <div class="info-row"><span class="k">日期</span><span class="v">{appointment_date}</span></div>
        <div class="info-row"><span class="k">时间</span><span class="v">{appointment_time}</span></div>
        <div class="info-row"><span class="k">方式</span><span class="v">{type_text} · 50 分钟</span></div>
        <div class="info-row"><span class="k">预约编号</span><span class="v">{appointment_no}</span></div>
      </div>
      <p><strong>来访者诉求</strong></p>
      <div class="info"><div class="info-row">{problem}</div></div>
      <div class="tip">请登录{EmailTemplate.BRAND_NAME}工作台，在「预约订单」中确认或婉拒这次预约。</div>
"""
        html_content = EmailTemplate.wrap(
            title="新的预约",
            body_html=body,
            preheader=f"{user_name} 预约了 {appointment_date} {appointment_time} 的咨询",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_appointment_reminder(
        email: str,
        nickname: str,
        counselor_name: str,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str,
    ) -> bool:
        """咨询即将开始提醒"""
        subject = f"【{EmailTemplate.BRAND_NAME}】咨询即将开始"

        type_map = {"video": "在线咨询", "voice": "在线咨询", "offline": "线下咨询"}
        type_text = type_map.get(consultation_type, "在线咨询")

        body = f"""
      <p>{nickname}，你好：</p>
      <p>你与 <strong>{counselor_name}</strong> 的咨询即将开始，提前准备一下会更从容。</p>
      <div class="info">
        <div class="info-row"><span class="k">日期</span><span class="v">{appointment_date}</span></div>
        <div class="info-row"><span class="k">时间</span><span class="v">{appointment_time}</span></div>
        <div class="info-row"><span class="k">方式</span><span class="v">{type_text} · 50 分钟</span></div>
      </div>
      <div class="tip">找一个安静、不被打扰的地方。开场前可以先想一想：这周最想聊的是什么。</div>
      <p class="muted">时间不合适的，也可以在「我的预约」里取消，不会产生任何费用。</p>
"""
        html_content = EmailTemplate.wrap(
            title="咨询即将开始",
            body_html=body,
            preheader=f"你与 {counselor_name} 的咨询 {appointment_date} {appointment_time} 开始",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_appointment_cancelled(
        email: str,
        nickname: str,
        appointment_date: str,
        appointment_time: str,
        reason: str = "",
    ) -> bool:
        """预约取消通知"""
        subject = f"【{EmailTemplate.BRAND_NAME}】预约已取消"

        reason_html = (
            f'<div class="info-row"><span class="k">取消原因</span><span class="v">{reason}</span></div>'
            if reason else ""
        )

        body = f"""
      <p>{nickname}，你好：</p>
      <p>以下这次咨询已取消：</p>
      <div class="info">
        <div class="info-row"><span class="k">日期</span><span class="v">{appointment_date}</span></div>
        <div class="info-row"><span class="k">时间</span><span class="v">{appointment_time}</span></div>
        {reason_html}
      </div>
      <div class="tip">取消不收取任何费用。想重新约时间的话，随时可以在「咨询预约」里再选一个时段。</div>
      <p class="muted">如果这是一次不太舒服的经历，也可以再试一次——换一位咨询师、换一个时间，都不算晚。</p>
"""
        html_content = EmailTemplate.wrap(
            title="预约已取消",
            body_html=body,
            preheader=f"{appointment_date} {appointment_time} 的咨询已取消",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_counselor_approval(email: str, name: str) -> bool:
        """咨询师申请通过通知"""
        subject = f"【{EmailTemplate.BRAND_NAME}】咨询师申请已通过"

        body = f"""
      <p>{name}老师，你好：</p>
      <p>你的咨询师申请已通过审核，从现在起可以在{EmailTemplate.BRAND_NAME}接待来访者了。</p>
      <p><strong>接下来可以做的事</strong></p>
      <div class="info">
        <div class="info-row"><span class="k">时段管理</span><span class="v">设置你能接待的时间</span></div>
        <div class="info-row"><span class="k">预约订单</span><span class="v">查看并确认来访者的预约</span></div>
        <div class="info-row"><span class="k">咨询会话</span><span class="v">到点后在这里与来访者沟通</span></div>
      </div>
      <div class="tip">建议先到「时段管理」发布你的真实可约时间。不设置的话，系统会按每天 09:00–19:00 展示默认时段。</div>
      <p class="muted">谢谢你的加入。{EmailTemplate.SLOGAN}</p>
"""
        html_content = EmailTemplate.wrap(
            title="申请已通过",
            body_html=body,
            preheader=f"{name}老师，你的咨询师申请已通过审核。",
        )
        return EmailService.send_email(email, subject, html_content)

    def send_counselor_rejection(email: str, name: str, reason: str = "") -> bool:
        """咨询师申请未通过通知"""
        subject = f"【{EmailTemplate.BRAND_NAME}】咨询师申请审核结果"

        reason_html = (
            f'<div class="info-row"><span class="k">说明</span><span class="v">{reason}</span></div>'
            if reason else ""
        )

        body = f"""
      <p>{name}老师，你好：</p>
      <p>感谢你申请成为{EmailTemplate.BRAND_NAME}的咨询师。经过审核，这次申请暂未通过。</p>
      {f'<div class="info">{reason_html}</div>' if reason else ''}
      <div class="tip">如果补充材料后愿意再次申请，我们随时欢迎。也可以在「帮助中心」了解我们的审核标准。</div>
      <p class="muted">无论如何，谢谢你愿意把时间给到需要帮助的人。</p>
"""
        html_content = EmailTemplate.wrap(
            title="申请审核结果",
            body_html=body,
            preheader=f"{name}老师，你的咨询师申请审核结果已出。",
        )
        return EmailService.send_email(email, subject, html_content)
