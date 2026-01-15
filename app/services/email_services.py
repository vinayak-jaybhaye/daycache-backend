from app.integrations.smtp import send_email
from app.utils.template_renderer import render_template
from app.services.redis_otp_service import VERIFICATION_TTL

def send_signup_otp(email: str, otp: str):
    body = render_template(
        "emails/otp_verification.txt",
        {
            "email": email,
            "otp": otp,
            "expiry": VERIFICATION_TTL // 60,  # minutes
        },
    )

    send_email(
        to_email=email,
        subject="Verify your DayCache account",
        body=body,
    )
