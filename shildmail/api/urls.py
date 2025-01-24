from django.urls import path
from django.contrib.auth.decorators import login_required

from shildmail.api import views
from shildmail.decorators import webauthn_login_required

urlpatterns = [
    path('login', views.api_login, name='api-login'),

    path('webauthn', login_required(views.api_webauthn), name='api-webauthn'),

    path('logout', login_required(views.api_logout), name='api-logout'),

    path('send-mail', webauthn_login_required(login_required(views.api_send_email)), name='api-send-email'),

    path('register', views.api_register, name='api-register'),

    path('register-device', views.api_register_webauthn_device, name='api-register-device'),

    path('add-device', webauthn_login_required(login_required(views.api_add_webauthn_device)), name='api-add-device'),

    path('password-generator', views.api_password_generator, name='api-password-generator'),

    path('ping', views.api_ping, name='api-ping'),
]
