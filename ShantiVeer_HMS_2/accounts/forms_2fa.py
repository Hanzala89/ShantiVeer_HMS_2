from __future__ import annotations

from django import forms


class OTPVerifyForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label="Verification code")


