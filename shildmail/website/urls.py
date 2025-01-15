
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import path

from shildmail.decorators import webauthn_login_required
from shildmail.website import views



urlpatterns = [
    path('', webauthn_login_required(login_required(views.home)), name='home'),
    path('login', views.login, name='login'),
    path('2fa', login_required(views.second_factor_authentication), name='second-factor-authentication'),
    path('register', views.register, name='register'),
    path('register-credentials', login_required(views.register_credentials), name='register-credentials'),
    path('mail', webauthn_login_required(login_required(views.mail)), name='create-mail'),
    # path('reply', webauthn_login_required(login_required( (views.mail_reply))), name='mail_reply'),
]
