from email.message import Message
from email import message_from_bytes
from email.header import decode_header
from typing import Dict
from email.message import Message


class Email:
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