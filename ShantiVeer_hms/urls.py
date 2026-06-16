from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('', include('accounts.urls')),
    path('', include('core.urls')),
    path('opd/', include('opd.urls')),
    path('ipd/', include('ipd.urls')),
    path('lab/', include('lab.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('prescription/', include('prescription.urls')),
    path('uhid/', include('uhid.urls')),
    path('master/', include('masterdata.urls')),
    path('income/', include('income.urls')),
    path('api/', include('core.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'ShantiVeer HMS Admin'
