from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from shildmail.website.forms import LoginForm
from django.contrib.auth import authenticate, login, logout

def api_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = "{PLAIN}" + form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            print(user)
            if(user):            # Zapisanie użytkownika w sesji
                login(request=request, user=user)
                # request.session['user'] = user
                return redirect('home')
            else: return JsonResponse({'message':"Invalid credentials"}, status=400)

    return HttpResponseBadRequest()

def api_register(request):
    return JsonResponse({'message': 'API register endpoint'})

def api_logout(request):
    logout(request)  # Wylogowuje użytkownika
    return HttpResponseRedirect(reverse('login'))

def api_send_email():
    return JsonResponse({'message': 'API Send mail'})


def api_ping(request):
    print(request.session.session_key,request.session.get('email'),request.session.items() )
    return JsonResponse({'session': request.session.session_key})


