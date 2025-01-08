import json
from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from webauthn import generate_authentication_options, generate_registration_options, options_to_json, verify_authentication_response, verify_registration_response
from shildmail.decorators import check_device_id
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
    PublicKeyCredentialDescriptor
)

from shildmail.cashe import memory_storage

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
        return redirect('home')
    else: return JsonResponse({'message':"Invalid credentials"}, status=400)


def api_register(request):
    return JsonResponse({'message': 'API register endpoint'})

def api_logout(request):
    imap_manager.close_connection(request.session.session_key)
    logout(request)  # Wylogowuje użytkownika
    return HttpResponseRedirect(reverse('login'))

def api_register_webauthn_device(request):
    if request.method == 'GET':
      simple_registration_options = generate_registration_options(
        rp_id=WEBAUTH_RP_ID,
        rp_name=WEBAUTH_RP_NAME,
        user_name=request.user.email,
      )

      request.session['challange'] = simple_registration_options.challenge.hex()

      options_json = json.loads(options_to_json(simple_registration_options))

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

      transports: list = body_json.get("transports", [])

      cred_to_store_in_db = {
          'username':request.user.email,
          'verification':verification,
          'transports':transports,
          'is_discoverable_credential':None,
      }

      print(cred_to_store_in_db) #credential_service
      memory_storage.set(request.user.email, cred_to_store_in_db) #credential_service

      return JsonResponse({"added":True})

def api_webauthn(request):
    if request.method == 'GET':

      stored_device = memory_storage.get(request.user.email)

      simple_authentication_options = generate_authentication_options(
         rp_id=WEBAUTH_RP_ID,
         allow_credentials=[PublicKeyCredentialDescriptor(id=stored_device['verification'].credential_id) ],
      )

      challange = simple_authentication_options.challenge.hex()
      request.session['challenge'] = challange
      
      memory_storage.set(challange, simple_authentication_options)

      response_json = json.loads(options_to_json(simple_authentication_options))

      return JsonResponse(response_json)
    else:
      body_json: dict = json.loads(request.body)
      credential = parse_authentication_credential_json(body_json)

      stored_device = memory_storage.get(request.user.email)
      challange = request.session['challenge']
      options = memory_storage.get(challange)


      verification = verify_authentication_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=WEBAUTH_RP_ID,
            expected_origin=WEBAUTH_ORIGIN,
            require_user_verification=False,
            credential_public_key=stored_device['verification'].credential_public_key,
            credential_current_sign_count=1,
      )

      print(verification)
      return JsonResponse({"verified": True})

def api_send_email():
    return JsonResponse({'message': 'API Send mail'})

@check_device_id
def api_ping(request):
    counter = request.session.get('counter',0) + 1
    request.session['counter'] = counter
    return JsonResponse({'email':request.session['email'], 'counter':counter })


