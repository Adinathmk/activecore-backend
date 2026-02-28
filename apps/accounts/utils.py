from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import EmailOTP
import secrets


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def create_and_send_otp(user, otp_type="verify"):

    # Invalidate previous unused OTPs of same type
    EmailOTP.objects.filter(
        user=user,
        otp_type=otp_type,
        is_used=False
    ).update(is_used=True)

    otp = generate_otp()
    otp_hash = make_password(otp)

    EmailOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        otp_type=otp_type
    )

    if otp_type == "reset":
        subject = "Reset your password"
        heading = "Password Reset"
    else:
        subject = "Verify your account"
        heading = "Email Verification"

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