import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.http import HttpRequest
from shildmail.settings import SMTP_HOST, SMTP_PORT
from shildmail.website.forms import MailForm


def send_mail(request:HttpRequest) -> bool:
    user = request.user
    print(user.password)
    print(user.email)

    mail_form = MailForm(request.POST)
    if(not mail_form.is_valid()):
        return False

    mail_data = mail_form.cleaned_data

    # Tworzenie wiadomości tekstowej
    message = MIMEText(mail_data['content'], "plain")  # "plain" oznacza zwykły tekst
    message["From"] = user.email
    message["To"] = mail_data['to']
    message["Subject"] =  mail_data['subject']

    # Wysyłanie e-maila
    try:
        # Połączenie z serwerem SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # Rozpoczęcie szyfrowania TLS
            server.login(user.email, user.password.replace('{PLAIN}',''))  # Logowanie do serwera
            server.sendmail(user.email, mail_data['to'], message.as_string())  # Wysłanie e-maila
            return True
    except Exception as e:
        return False