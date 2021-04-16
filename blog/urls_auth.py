# Project: blog_7myon_com
# Package: 
# Filename: auth_urls.py
# Generated: 2021 Jan 25 at 17:00 
# Description of <auth_urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.contrib.auth.urls import urlpatterns as auth_urlpatterns
from django.urls import path

from .views.base import auth

# path('login/', views.LoginView.as_view(), name='login'),
# path('logout/', views.LogoutView.as_view(), name='logout'),
#
# path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
# path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
#
# path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
# path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
# path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
# path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

auth_urls = [
    path('registration/', auth.RegistrationView.as_view(), name='user_registration'),
    path('registration/done/', auth.RegistrationDoneView.as_view(), name='user_registration_done'),
    path(
        'registration/confirm/<uidb64>/<token>/',
        auth.RegistrationConfirmView.as_view(),
        name='user_registration_confirm'
    ),
]

# we need to redefine all of view where success url is hardcoded for reverse
# for using the blog:some_success_viewname
auth_urls_overrides = {
    'password_reset': auth.PasswordResetView.as_view(),
    'password_reset_confirm': auth.PasswordResetConfirmView.as_view(),
    'password_change': auth.PasswordChangeView.as_view(),
    'login': auth.LoginView.as_view(),
}

for pattern in auth_urlpatterns:
    if pattern.name in auth_urls_overrides:
        pattern = path(str(pattern.pattern), auth_urls_overrides[pattern.name], name=pattern.name)
    auth_urls.append(pattern)

urlpatterns = [
    *auth_urls
]
