from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


urlpatterns = [
    path('admin/', admin.site.urls),

    #flatpages
    path('about/', include('django.contrib.flatpages.urls')),

    #password reset
    path('settings/privacy/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('settings/privacy/password_reset/done/',PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('settings/privacy/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('settings/privacy/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Mechinpy App
    path('', include('bidhanblog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)