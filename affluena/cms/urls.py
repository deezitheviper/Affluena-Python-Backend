
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/', include('accounts.urls')),
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('staff-login',views.user_login, name='login'),
    path('staff-logout',views.user_logout, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='reset_password'),
    path('password-sent/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('confirm-password/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-changed/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),name='password_reset_complete')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 