# import resend
# from app.core.config import Settings

# # Set Resend API key from settings
# RESEND_API_KEY = Settings().RESEND_API_KEY
# resend.api_key = RESEND_API_KEY

# def send_email(to_email: str, subject: str, body: str):
#     """
#     Sends an email using the Resend API.

#     Args:
#         to_email (str): Recipient's email address.
#         subject (str): Email subject line.
#         body (str): HTML content of the email.

#     Returns:
#         dict: Response from Resend API.
#     """
#     try:
#         # Email parameters
#         params = {
#             "from": "DayCache <daycache@resend.dev>",  # Ensure the domain is verified
#             "to": [to_email],
#             "subject": subject,
#             "html": body,
#         }

#         # Send email
#         response = resend.Emails.send(params)

#         # Success log
#         print(f"✅ Email sent successfully: {response}")
#         return response

#     except Exception as e:
#         # Error log
#         print(f"❌ Error sending email: {e}")
#         raise e


## Using SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import Settings

SMTP_SERVER = Settings().SMTP_SERVER
SMTP_PORT =  Settings().SMTP_PORT
SMTP_USERNAME = Settings().SMTP_USERNAME
SMTP_PASSWORD = Settings().SMTP_PASSWORD

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
