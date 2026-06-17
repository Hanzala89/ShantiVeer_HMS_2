from django.contrib import admin
from .models import Bed, Notification


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['room_no', 'bed_no', 'status', 'patient']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
