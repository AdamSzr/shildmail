from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.decorators import login_required

from shildmail.api import views

urlpatterns = [
    path('login', views.api_login, name='api-login'),

    path('webauthn', login_required(views.api_webauthn), name='api-webauthn'), # get - returns options, post makes verification

    path('logout', login_required(views.api_logout), name='api-logout'),

    path('send-mail', login_required(views.api_send_email), name='api-send-email'),

    path('register', views.api_register, name='api-register'),

    path('register-device', login_required(views.api_register_webauthn_device), name='api-register-device'), # get - returns challange, post saves data

    path('ping', views.api_ping, name='api-ping'),
]
