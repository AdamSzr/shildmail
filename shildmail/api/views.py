import json
from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from webauthn import generate_authentication_options, generate_registration_options, options_to_json, verify_authentication_response, verify_registration_response
from shildmail.decorators import webauthn_login_required
from shildmail.models.passkeys import WebAuthnCredential, WebAuthnCredentialManager
from shildmail.models.user import User
from shildmail.settings import WEBAUTH_ORIGIN, WEBAUTH_RP_ID, WEBAUTH_RP_NAME
from shildmail.website.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from shildmail.imap.manager import imap_manager
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from webauthn.helpers import (
    base64url_to_bytes,
    parse_registration_credential_json,
    parse_registration_options_json,
    parse_authentication_credential_json
)

from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    AuthenticatorTransport,
)


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
    if(user):  # Zapisanie użytkownika w sesji
        login(request=request, user=user)
        request.session['email'] = email

        hasKeys = WebAuthnCredential.objects.filter(username=email).exists()

        if(hasKeys): return redirect('2fa')
        else: return redirect('register-credentials')

    else: return JsonResponse({'message':"Invalid credentials"}, status=400)


def api_register(request):
    return JsonResponse({'message': 'API register endpoint'})

def api_logout(request):
    imap_manager.close_connection(request.session.session_key)
    logout(request)  # Wylogowuje użytkownika
    return HttpResponseRedirect(reverse('login'))

def api_register_webauthn_device(request):
    if request.method == 'GET':
      credentials = WebAuthnCredential.objects.filter(username=request.user.email)

      registration_options = generate_registration_options(
        rp_id=WEBAUTH_RP_ID,
        rp_name=WEBAUTH_RP_NAME,
        user_name=request.user.email,
        exclude_credentials=[
            PublicKeyCredentialDescriptor(
              id=credential.credential_id,
              type= PublicKeyCredentialType(credential.credential_type),
              transports=[ AuthenticatorTransport(trans) for trans in credential.transports ]
            )
            for credential in credentials
        ]
      )

      request.session['challange'] = registration_options.challenge.hex()

      options_json = json.loads(options_to_json(registration_options))

      options_json["extensions"] = {
        "credProps": True,
      }

      return JsonResponse(options_json)
    else:
      body_json: dict = json.loads(request.body)

      credential = parse_registration_credential_json(body_json)

      verification = verify_registration_response(
          credential=credential,
          expected_challenge=bytes.fromhex(request.session['challange']),
          expected_rp_id=WEBAUTH_RP_ID,
          expected_origin=WEBAUTH_ORIGIN,
          require_user_verification=False,
      )

      new_passkey = WebAuthnCredential.objects.create(
          username=request.user.email,
          credential_id=verification.credential_id,
          credential_public_key=verification.credential_public_key,
          credential_type=verification.credential_type,
          aaguid=verification.aaguid,
          transports=body_json['response'].get("transports", []),
          is_discoverable=True,
          sign_count=verification.sign_count,
          authenticator_attachment=body_json['authenticatorAttachment'],
          public_key_algorithm=body_json['response'].get("publicKeyAlgorithm", 0),
      )

      new_passkey.save()

      return JsonResponse({"added":True})

def api_webauthn(request):
    if request.method == 'GET':
      credentials = WebAuthnCredential.objects.filter(username=request.user.email)

      authentication_options = generate_authentication_options(
        rp_id=WEBAUTH_RP_ID,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=credential.credential_id)
            for credential in credentials
        ],
      )

      request.session['challenge'] = authentication_options.challenge.hex()

      response_json = json.loads(options_to_json(authentication_options))

      return JsonResponse(response_json)
    else:
      body_json: dict = json.loads(request.body)
      credential = parse_authentication_credential_json(body_json)
      db_credential = WebAuthnCredential.objects.filter(username=request.user.email, credential_id=credential.raw_id).first()

      challenge = request.session['challenge']

      verification = verify_authentication_response(
            credential=credential,
            expected_challenge=bytes.fromhex(challenge),
            expected_rp_id=WEBAUTH_RP_ID,
            expected_origin=WEBAUTH_ORIGIN,
            credential_public_key=db_credential.credential_public_key,
            credential_current_sign_count=db_credential.sign_count,
      )

      print(verification)

      WebAuthnCredential.objects.increment_sign_count(credential_id=credential.raw_id)

      request.session['credential_id'] = credential.id

      return JsonResponse({"verified": True})

def api_send_email():
    return JsonResponse({'message': 'API Send mail'})

# @check_device_id
def api_ping(request):
    # Znajdź użytkownika po adresie e-mail
    user_email = "simple@adamszreiber.pl"

    # # Utwórz nowe poświadczenie dla tego użytkownika
    # new_passkey = WebAuthnCredential.objects.create(
    #     username=user_email,  # Możesz ustawić username jako email użytkownika
    #     credential_id=b'\x01\x02\x03\x04',  # Przykładowy identyfikator poświadczenia (binarny)
    #     credential_public_key=b'\x01\x02\x03\x04\x05',  # Przykładowy klucz publiczny (binarny)
    #     credential_type='public_key',  # Typ poświadczenia
    #     aaguid='12345678-1234-1234-1234-123456789012',  # AAGUID (przykładowy)
    #     transports=['usb', 'nfc'],  # Lista dostępnych transportów
    #     is_discoverable=True,  # Możliwość wykrywania poświadczenia
    #     sign_count=0,  # Początkowa liczba podpisów
    #     authenticator_attachment='platform',  # Typ urządzenia (platforma)
    #     public_key_algorithm=1,  # Przykładowy algorytm klucza publicznego
    # )

    # new_passkey.save()

    credentials = WebAuthnCredential.objects.filter(username=user_email).first()
    WebAuthnCredential.objects.increment_sign_count(credential_id=credentials.credential_id)

    return JsonResponse({'email':'abc' })


