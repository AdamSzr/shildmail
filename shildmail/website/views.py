import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from shildmail.imap.manager import imap_manager
from shildmail.website.forms import LoginForm


def home(request):
    return render(request, 'home.html',{'name':'login'})

def login(request):
    if(request.user.is_authenticated):
        return redirect('home')

    return render(request, 'login.html', {'form': LoginForm()})

def register(request):
    return render(request, 'home.html',{'name':'register'})


def test(request):
    id = request.session.session_key
    email = request.user.email
    password = request.user.password.replace('{PLAIN}','')
    print(email,password)
    connection = imap_manager.create_connection(id,email,password)
    (stat,data) = connection.noop()
    print(stat,data)
    print(imap_manager.connections)
    return HttpResponse(stat)
