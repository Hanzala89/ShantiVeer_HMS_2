from django.urls import path
from . import views
from . import backup_views

app_name = 'core'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='notifications_read_all'),

    # Bed Management
    path('beds/', views.bed_manage, name='bed_manage'),
    path('beds/add/', views.bed_add, name='bed_add'),
    path('beds/<int:pk>/edit/', views.bed_edit, name='bed_edit'),
    path('beds/<int:pk>/delete/', views.bed_delete, name='bed_delete'),

    # Data Backup
    path('backup/', backup_views.backup_dashboard, name='backup'),
    path('backup/now/', backup_views.backup_now, name='backup_now'),
    path('backup/schedule/', backup_views.backup_schedule_save, name='backup_schedule_save'),
    path('backup/<int:pk>/download/', backup_views.backup_download, name='backup_download'),
    path('backup/<int:pk>/delete/', backup_views.backup_delete, name='backup_delete'),
]