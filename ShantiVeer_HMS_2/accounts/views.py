import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache

from .forms import StyledLoginForm, ForgotPasswordForm, StyledPasswordChangeForm, StyledSetPasswordForm, ChangeEmailForm
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = getattr(settings, 'LOGIN_ATTEMPTS_LIMIT', 5)
_LOCKOUT_SECONDS = getattr(settings, 'LOGIN_LOCKOUT_DURATION', 300)


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


def _is_locked(ip):
    return bool(cache.get(f'hms:login_lock:{ip}'))


def _record_failure(ip):
    key = f'hms:login_fail:{ip}'
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=_LOCKOUT_SECONDS)
    if attempts >= _MAX_ATTEMPTS:
        cache.set(f'hms:login_lock:{ip}', True, timeout=_LOCKOUT_SECONDS)
        logger.warning('Login locked for IP %s after %d failed attempts', ip, attempts)


def _clear_failures(ip):
    cache.delete(f'hms:login_fail:{ip}')
    cache.delete(f'hms:login_lock:{ip}')


def login_view(request):
    """Login with username and password only — no 2FA."""
    if request.user.is_authenticated:
        return redirect('core:home')

    ip = _get_ip(request)
    if _is_locked(ip):
        messages.error(request, 'Too many failed login attempts. Please try again later.')
        return render(request, 'accounts/login.html', {'form': StyledLoginForm(), 'locked': True})

    form = StyledLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            _clear_failures(ip)
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('core:home')
        else:
            _record_failure(ip)

    return render(request, 'accounts/login.html', {'form': form})


def login_2fa_view(request):
    """2FA removed — redirect to login."""
    return redirect('accounts:login')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        users = User.objects.filter(email__iexact=email)
        if users.exists():
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse_lazy('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                try:
                    send_mail(
                        subject='SantiVeer HMS — Password Reset',
                        message=f'Click to reset your password:\n{reset_url}\n\nLink expires in 24 hours.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error('Password reset email failed for user %s: %s', user.username, e)
        messages.success(request, 'If that email is registered, a password reset link has been sent.')
        return redirect('accounts:password_reset_done')
    return render(request, 'accounts/forgot_password.html', {'form': form})


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


@login_required
def change_email_view(request):
    form = ChangeEmailForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.email = form.cleaned_data['new_email']
        request.user.save()
        messages.success(request, 'Your email address has been updated successfully.')
        return redirect('accounts:change_password')
    return render(request, 'accounts/change_email.html', {'form': form})


@login_required
def change_password_view(request):
    form = StyledPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password has been changed successfully.')
        return redirect('core:home')
    return render(request, 'accounts/change_password.html', {'form': form})