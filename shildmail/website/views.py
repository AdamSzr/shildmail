from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from shildmail.website.forms import LoginForm


def home(request):
    return render(request, 'home.html',{'name':'login'})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Próba uwierzytelnienia użytkownika
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Successfully logged in!")
                return redirect('/')  # Przekierowanie na stronę główną
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def register(request):
    return render(request, 'home.html',{'name':'register'})


numbers = []

def test(request):
    print(request.session_data)
    random_num = random.randint(0,100)  # Losowa liczba z zakresu 1-100
    numbers.append(random_num)
    response =  JsonResponse({'random_number': random_num, 'numbers':numbers})
    response.set_cookie('x-test',1,120)
    return response
