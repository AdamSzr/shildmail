from datetime import datetime
from email.message import Message
from email import message_from_bytes
from email.header import decode_header
import random
from typing import Dict
from email.message import Message


class Email:


    # def __init__(self):
    #     self.raw = b''  # Przechowujemy całą surową wiadomość
    #     self.subject = 'Sprawdź status swojej płatności'
    #     self.sender = 'service@payu.com'
    #     self.recipient = 'simple@adamszreiber.pl'
    #     self.date_sent = 'Thu, 09 Jan 2025 13:24:56 -0800'
    #     self.message_id = '<67803ea8.a70a0220.1f1e4b.c845SMTPIN_ADDED_MISSING@mx.google.com>'
    #     self.content = 'w związku ze zbliżającym się terminem przygotowania informacji podatkowej PIT-8C prosimy o sprawdzenie, czy Państwa dane osobowe i adresowe posiadane przez XTB S.A. są aktualne.'


    def __init__(self, raw_msg):
        self.raw = raw_msg  # Przechowujemy całą surową wiadomość
        self.subject = self._get_subject()
        self.sender = self.raw.get("From")
        self.recipient = self.raw.get("To")
        self.date_sent = self.raw.get("Date")
        self.message_id = self.raw.get("Message-ID")
        self.content = self._get_content()

    def _get_subject(self) -> str:
        """Parsowanie tematu wiadomości"""
        subject, encoding = decode_header(self.raw["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        return subject

    def _get_content(self) -> str:
        """Parsowanie treści wiadomości"""
        content = ""
        if self.raw.is_multipart():
            for part in self.raw.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":  # Tylko wiadomości tekstowe
                    content = part.get_payload(decode=True).decode("utf-8")
                    break
        else:
            try:
            # Jeśli wiadomość nie jest multipart
                content = self.raw.get_payload(decode=True).decode("utf-8", errors="replace")
            except (UnicodeDecodeError, TypeError):
                content = "Błąd dekodowania treści"

        return content
    


    def format_date(self, input_date:str):
        try:
            return datetime.strptime(input_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%d.%m.%Y %H:%M")
        except:
            return input_date
    
    def to_dict(self):
        return {
            'raw':self.raw,
            'subject':self.subject,
            'sender':self.sender,
            'recipient':self.recipient,
            'date_sent':self.format_date(self.date_sent),
            'message_id':self.message_id,
            'content':self.content,
        }
