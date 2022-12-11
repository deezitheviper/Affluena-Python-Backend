from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email
from .views import *
from rest_auth.registration.views import  RegisterView 
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from .cms import views
from django.views.generic import RedirectView
from rest_auth.views import UserDetailsView
from .views import EmailChallengeRequestDetail, EmailChallengeVerifyDetail, RegisterView,PhoneRequestDetail,PhoneVerifyDetail
from django.contrib.auth import views as auth_views
from rest_auth.views import PasswordResetConfirmView


urlpatterns = [ 
    
    path('account/', include('accounts.urls')),
    path('staff-board', views.home, name='board'),
    path('phonerequest/',PhoneRequestDetail.as_view() ),
    path('phoneverifyrequest/',PhoneVerifyDetail.as_view() ),
    path('staff-login',views.user_login, name='login'),
    path('register', views.register, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='cms/password_reset_form.html'), name='reset_password'),
    path('password-sent/', auth_views.PasswordResetDoneView.as_view(template_name='cms/password_reset_done.html'), name='password_reset_done'),
    path('confirm-password/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='cms/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-changed/', auth_views.PasswordResetCompleteView.as_view(template_name='cms/password_reset_complete.html'),name='password_reset_complete'),
    path('staff-logout',views.user_logout, name='logout'),
    re_path(r"^mfa/authtoken/", include((
    "affluena.authToken.urls",'app_name'), namespace="mfa-authtoken:login")),
    path("email/request/",EmailChallengeRequestDetail.as_view(),
    name="your_challenge_method_request-detail"
),
    path("email/verify/",EmailChallengeVerifyDetail.as_view(),
    name="your_challenge_method_verify-detail"),
    path('user-detail/', UserDetailsView.as_view()),
    path('contact-us/', Contact.as_view(), name='contact-us'),
    path('mail/', EmailView.as_view()),
    re_path(r'update-profile/(?P<pk>\d+)/', UserPartialUpdateView.as_view(), name="updateProfile"),
    path('auth/registration/', RegisterView.as_view(), name='rest_register' ),
    re_path(r'^rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/',include('affluena.api.urls')),
    path('resend-verification-email/', NewEmailConfirmation.as_view(), name='resend-email-confirmation'),
    path('password/reset/', PasswordResetView.as_view(),
        name='rest_password_reset'),
    re_path(r'^account-confirm-email/', VerifyEmailView.as_view(),
     name='account_email_verification_sent'), 
    path('admin/', admin.site.urls),
    re_path(r'user/*', TemplateView.as_view(template_name='indeex.html')),
    re_path(r'password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})',
        TemplateView.as_view(template_name='index.html'),
        name='password_reset_confirm')
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path('', TemplateView.as_view(template_name='index.html'), name="home")]