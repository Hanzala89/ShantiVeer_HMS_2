from django.conf import settings
from core import services


def hospital_info(request):
    ctx = {
        'hospital_name': settings.HOSPITAL_NAME,
        'hospital_address': settings.HOSPITAL_ADDRESS,
        'hospital_phone': settings.HOSPITAL_PHONE,
    }
    if request.user.is_authenticated:
        ctx['unread_notifications'] = services.get_unread_notifications(request.user, limit=5)
        ctx['notification_count'] = services.get_unread_notification_count(request.user)
    else:
        ctx['unread_notifications'] = []
        ctx['notification_count'] = 0
    return ctx
