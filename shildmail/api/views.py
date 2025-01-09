import json
from pyexpat.errors import messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from webauthn import generate_authentication_options, generate_registration_options, options_to_json, verify_authentication_response, verify_registration_response
from shildmail.imap.IMAP_Adapter import IMAPAdapter
from shildmail.models.passkeys import WebAuthnCredential
from shildmail.models.user import User
from shildmail.settings import WEBAUTH_ORIGIN, WEBAUTH_RP_ID, WEBAUTH_RP_NAME
from shildmail.smtp.send_mail import send_mail
from shildmail.website.forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from shildmail.imap.manager import imap_manager
from webauthn.helpers import (
    parse_registration_credential_json,
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

        if(hasKeys): return redirect('second-factor-authentication')
        else: return redirect('register-credentials')

    else: return JsonResponse({'message':"Invalid credentials"}, status=400)


def api_register(request):
    if(request.method!='POST'):
      return JsonResponse({'result':False, 'message': 'invalid http method'})

    form = RegisterForm(request.POST)

    if(not form.is_valid()):
      return JsonResponse({'result':False, 'message': 'Form validatioin'})

    data = form.cleaned_data
    if User.objects.filter(email=data['username']).exists():
        return JsonResponse({'result':False, 'message': 'Email already taken'})

    user = User.objects.create(
       email=data['username'],
       realname=data['realname'],
       password=data['password'],
       maildir=data['realname'].lower().replace(' ', '_') + '/'
    )
    print(user)
    return JsonResponse({'result':True})


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

      WebAuthnCredential.objects.increment_sign_count(credential_id=credential.raw_id)

      request.session['credential_id'] = credential.id

      return JsonResponse({"verified": True})

def api_send_email(request:HttpRequest):
    if(request.method != 'POST'):
      return JsonResponse({'result':False, 'message': 'wrong http method'})

    if(send_mail(request)): return JsonResponse({'result':True})
    else: return JsonResponse({ 'result':False, 'message': 'SMTP Error'})

# @check_device_id
def api_ping(request:HttpRequest):
    return JsonResponse({'email':'abc' })


