import aiosmtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from app import config


def load_and_render_template(template_filename, **kwargs):
    """
    使用 Jinja2 渲染模板
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(current_dir))
    template = env.get_template(template_filename)
    return template.render(**kwargs)


async def send_email(to_email: str, subject: str, code: str, template_filename: str="email_verification.html"):
    """
    异步发送邮件（支持 QQ 邮箱 SMTP）
    """
    try:
        message = MIMEMultipart("alternative")
        message["From"] = config.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject

        # 加载并渲染模板
        html_content = load_and_render_template(
            template_filename=template_filename,
            code=code,
            expiry_minutes=config.VERIFICATION_CODE_TTL // 60
        )

        mime_text = MIMEText(html_content, "html", "utf-8")
        message.attach(mime_text)

        await aiosmtplib.send(
            message,
            hostname=config.SMTP_SERVER,
            port=config.SMTP_PORT,
            username=config.SMTP_USER,
            password=config.SMTP_PASSWORD,
            use_tls=True
        )
        return True, "邮件发送成功"

    except aiosmtplib.SMTPServerDisconnected:
        return False, "与邮件服务器的连接意外断开，请检查SMTP配置"
    except aiosmtplib.SMTPError as e:
        return False, f"邮件发送失败: {str(e)}"
    except Exception as e:
        return False, f"发生未知错误: {str(e)}"
