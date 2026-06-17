"""Two-factor (email + terminal OTP) helpers for accounts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TwoFactorConfig:
    enabled: bool = True
    otp_ttl_seconds: int = 300
    otp_length: int = 6

