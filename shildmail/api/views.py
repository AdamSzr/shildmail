from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from shildmail.website.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from shildmail.imap.manager import imap_manager
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

def api_login(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    form = LoginForm(request.POST)

    if form.is_valid() == False:
        return JsonResponse({'message':"Invalid credentials"}, status=400)

    email = form.cleaned_data['email']
    password = "{PLAIN}" + form.cleaned_data['password']
    user = authenticate(request, email=email, password=password)

    print(user)
    if(user):            # Zapisanie użytkownika w sesji
        login(request=request, user=user)
        return redirect('home')
    else: return JsonResponse({'message':"Invalid credentials"}, status=400)


def api_register(request):
    return JsonResponse({'message': 'API register endpoint'})

def api_logout(request):
    imap_manager.close_connection(request.session.session_key)
    logout(request)  # Wylogowuje użytkownika
    return HttpResponseRedirect(reverse('login'))

def api_send_email():
    return JsonResponse({'message': 'API Send mail'})


def api_ping(request):
    # Generowanie kluczy RSA (tylko w celach demonstracyjnych)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Wiadomość do podpisania
    message = b"This is a secret message"

    # Podpisanie wiadomości kluczem prywatnym
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Weryfikacja podpisu kluczem publicznym
    try:
        public_key.verify(
            signature,
            message+b'1',
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Wiadomość została pomyślnie zweryfikowana!")
    except Exception as e:
        print(f"Weryfikacja nie powiodła się: {e}")

    return JsonResponse({'session': request.session.session_key, 'message_raw':message.decode(), 'message_to_ver': (message+b'1').decode() })


