
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import path

from shildmail.website import views



urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('register-credentials', views.register_credentials, name='register-credentials'),

    path('test', views.test, name="test"),
]
