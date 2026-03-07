from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from .models import UserOTP
from twilio.rest import Client
import secrets
import logging

logger = logging.getLogger(__name__)

client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)


# ==============================
# 🔹 Generate Secure OTP
# ==============================
def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


# ==============================
# 🔹 Send WhatsApp OTP
# ==============================
def send_whatsapp_otp(phone_number, otp):
    try:
        message = client.messages.create(
            body=f"Your OTP is: {otp}. It expires in 5 minutes.",
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone_number}"
        )
        logger.info(f"WhatsApp OTP sent to {phone_number}. SID: {message.sid}")
        return message.sid
    except Exception as e:
        logger.error(f"WhatsApp OTP failed: {str(e)}")
        raise


# ==============================
# 🔹 Send Email OTP
# ==============================
def send_email_otp(user, otp, subject, heading):
    text_content = f"Your verification code is: {otp}\nThis code expires in 5 minutes."

    html_content = f"""
        <h2>{heading}</h2>
        <p>Your verification code is:</p>
        <h1 style="letter-spacing: 3px;">{otp}</h1>
        <p>This code expires in 5 minutes.</p>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
    logger.info(f"Email OTP '{subject}' sent to {user.email}")


# ==============================
# 🔹 Main OTP Service
# ==============================
def create_and_send_otp(user, otp_type="verify", channel="email"):

    # Invalidate previous unused OTPs
    UserOTP.objects.filter(
        user=user,
        otp_type=otp_type,
        is_used=False
    ).update(is_used=True)

    otp = generate_otp()
    otp_hash = make_password(otp)

    # Save OTP with channel
    UserOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        otp_type=otp_type,
        channel=channel
    )

    if otp_type == "reset":
        subject = "Reset your password"
        heading = "Password Reset"
    else:
        subject = "Verify your account"
        heading = "Email Verification"

    # Send via selected channel
    if channel == "email":
        send_email_otp(user, otp, subject, heading)

    elif channel == "whatsapp":
        if not user.phone_number:
            raise ValueError("User does not have phone number")
        send_whatsapp_otp(user.phone_number, otp)

    else:
        raise ValueError("Invalid OTP channel")