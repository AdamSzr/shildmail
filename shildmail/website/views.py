import logging
import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import email
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from shildmail.imap.manager import imap_manager
from shildmail.website.forms import LoginForm, MailForm, RegisterForm
from email.header import decode_header


def home(request):
    return render(request, 'home.html',{'name':'login'})

def login(request):
    return render(request, 'login.html', {'form': LoginForm()})

def second_factor_authentication(request):
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

def test(request):
    # id = request.session.session_key
    # email = request.user.email
    # password = request.user.password.replace('{PLAIN}','')
    # print(email,password)
    id = '1234'
    connection = imap_manager.create_connection(id,'simple@adamszreiber.pl','simple')
    status, folders = connection.list()

    regex = re.compile(r'\(.+\) "." (?P<dir_name>\w+)')

    # Wyciągnięcie `dir_name` z każdego wpisu
    dir_names = [match.group('dir_name') for folder in folders if (match := regex.search(folder.decode()))]

    if status == 'OK':
       print(dir_names)



    status, response = connection.select('INBOX')

    print(status, response)

  # Pobranie numerów wiadomości (wszystkie wiadomości)
    status, message_numbers = connection.search(None, "ALL")
    if status != 'OK':
        print("Nie udało się wyszukać wiadomości.")
        exit()

    # Iteracja po każdej wiadomości
    for num in message_numbers[0].split():
        # Pobranie wiadomości
        print('Pobieranie wiadomości nr -> '+ num.decode())
        status, msg_data = connection.fetch(num, '(RFC822.HEADER)')
        if status != 'OK':
            print(f"Nie udało się pobrać wiadomości nr {num.decode()}.")
            continue

        # Analiza nagłówków wiadomości
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Wyciąganie nagłówków
                subject = decode_mime_words(msg["Subject"]) if msg["Subject"] else "(Brak tematu)"
                from_ = decode_mime_words(msg["From"]) if msg["From"] else "(Brak nadawcy)"
                date = msg["Date"] if msg["Date"] else "(Brak daty)"

                # Wyświetlanie nagłówków
                print(f"Temat: {subject}")
                print(f"Nadawca: {from_}")
                print(f"Data: {date}")
                print("-" * 50)

    print(status, message_numbers)

    imap_manager.delete_connection(id)

    return HttpResponse('done')
