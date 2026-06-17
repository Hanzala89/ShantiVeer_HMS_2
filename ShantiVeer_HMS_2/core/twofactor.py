"""Lightweight email + in-memory OTP verification (2-step login helper).

Uses secrets module for cryptographically secure OTP generation.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail


OTP_CACHE_PREFIX = "hms:otp:"


@dataclass(frozen=True)
class OTPSendResult:
    email: str
    sent: bool


def _otp_cache_key(user_id: int) -> str:
    return f"{OTP_CACHE_PREFIX}{user_id}"


def generate_otp(*, user_id: int, ttl_seconds: int = 300, length: int = 6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    otp = "".join(str(secrets.randbelow(10)) for _ in range(length))
    cache.set(_otp_cache_key(user_id), otp, timeout=ttl_seconds)
    # DEV convenience: optionally print OTP to terminal/logs
    if getattr(settings, "PRINT_OTP_TO_TERMINAL", True):
        # Developer convenience: print OTP regardless of DEBUG
        # (you can disable by setting PRINT_OTP_TO_TERMINAL=false)
        print(f"[HMS OTP] user_id={user_id} otp={otp}")

    return otp


def get_cached_otp(*, user_id: int) -> Optional[str]:
    return cache.get(_otp_cache_key(user_id))


def clear_cached_otp(*, user_id: int) -> None:
    cache.delete(_otp_cache_key(user_id))


def send_otp_email(*, to_email: str, otp: str) -> OTPSendResult:
    subject = "SantiVeer HMS — Verification Code"
    msg = (
        f"Your verification code is: {otp}\n\n"
        "Enter this code to complete login. "
        "This code is valid for 5 minutes.\n\n"
        "If you did not request this, please ignore this email."
    )

    sent = True
    try:
        send_mail(
            subject=subject,
            message=msg,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[to_email],
            fail_silently=True,
        )
    except Exception:
        sent = False

    return OTPSendResult(email=to_email, sent=sent)
