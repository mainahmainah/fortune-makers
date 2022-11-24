from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.contrib.auth import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # path('ehub-secret/', admin.site.urls),
    # path('ehub-backdoor/', admin.site.urls),
    # path('', IndexPageView.as_view(), name='index'),
    path('', include('fortune.urls')),
    # path('', include('main.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    ]

