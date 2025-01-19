from email.message import Message
import logging
import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import email
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from shildmail.imap.email import Email
from shildmail.imap.manager import imap_manager
from shildmail.models.passkeys import WebAuthnCredential
from shildmail.website.forms import LoginForm, MailForm, RegisterForm
from email.header import decode_header

from shildmail.website.page_props import HomePageProps



def home(request):
    props = HomePageProps(request)
    return render(request, 'home.html',props.to_dict())

def login(request):
    return render(request, 'login.html', {'form': LoginForm()})

def second_factor_authentication(request):
    hasKeys = WebAuthnCredential.objects.filter(username=request.user.email).exists()

    if(not hasKeys): return redirect('register-credentials')

    return render(request, 'second_factor_authentication.html')

def register(request):
    return render(request, 'register.html',{'form':RegisterForm()})

def register_credentials(request):
    return render(request, 'register_credentials.html',{'name':'register credentials'})


def decode_mime_words(s):
    """
    Dekodowanie nagłówków MIME (np. tematu, nadawcy) do czytelnego tekstu.
    """
    decoded = decode_header(s)
    return ''.join(
        part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
        for part, charset in decoded
    )

def mail(request):
    return render(request, 'create_mail.html', {'form': MailForm()})



def mail_reply(request):
    message_id= request.GET.get('message_id')
    mailbox = request.GET.get('mailbox')
    # Pobranie wiadomości z bazy danych
    mail = {
        'subject':'subject',
        'sender':'sender',
        'recipient':'recipient',
        'date_sent':'date_sent',
        'content':'content',
        'message_id':'message_id'
    }

    # Przekazanie wiadomości do szablonu
    return render(request, 'mail_detail.html', {'mail': mail})
