import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str) -> None:
    # msg = MIMEMultipart()
    # msg["From"] = settings.SMTP_USERNAME
    # msg["To"] = to_email
    # msg["Subject"] = subject

    # msg.attach(MIMEText(body, "plain"))

    # try:
    #     with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
    #         server.starttls()
    #         server.login(
    #             settings.SMTP_USERNAME,
    #             settings.SMTP_PASSWORD,
    #         )
    #         server.sendmail(
    #             settings.SMTP_USERNAME,
    #             to_email,
    #             msg.as_string(),
    #         )
    # except Exception as exc:
    #     logger.exception("Failed to send email")
    #     raise

    print(f"Sending email to {to_email} with subject '{subject}' and body:\n{body}")
    
