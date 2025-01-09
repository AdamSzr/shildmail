from imaplib import IMAP4_SSL
import email
from email.header import decode_header
from typing import List, Dict, Optional

from shildmail.settings import IMAP_HOST, IMAPS_PORT



class IMAPAdapter:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.mailbox: str|None = None
        self.connection: IMAP4_SSL | None = None
        self.mailboxes: List[str] | None = None

    def connect(self):
        """
        Łączy się z serwerem IMAP i loguje.
        """
        self.connection = IMAP4_SSL(IMAP_HOST, IMAPS_PORT)
        self.connection.login(self.username, self.password)

    def disconnect(self):
        """
        Zamyka połączenie z serwerem IMAP.
        """
        if self.connection:
            self.connection.close()
            self.connection.logout()
            self.connection = None

    def check_connection(self):
        if not self.connection:
            raise RuntimeError("Not connected to IMAP server.")


    def _decode_header(self, header: str) -> str:
        """
        Dekoduje nagłówki wiadomości e-mail, np. tytuły lub nadawcę.
        """
        decoded_header = decode_header(header)
        decoded_parts = []
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or "utf-8"))
            else:
                decoded_parts.append(part)
        return "".join(decoded_parts)

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Zwraca listę wiadomości z datą, tytułem i nadawcą.
        """
        self.check_connection()

        status, messages = self.connection.search(None, "ALL")
        if status != "OK":
            return []

        messages_list = []
        for msg_id in messages[0].split():
            status, msg_data = self.connection.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Dekodowanie pól
            date = email_message.get("Date")
            subject = self._decode_header(email_message.get("Subject"))
            from_ = self._decode_header(email_message.get("From"))

            messages_list.append({
                "date": date,
                "subject": subject,
                "from": from_,
                "id": msg_id.decode("utf-8")
            })

        return messages_list

    def get_message(self, msg_id: str) -> Optional[Dict[str, str]]:
        """
        Zwraca szczegóły wiadomości o podanym ID.
        """
        self.check_connection()

        status, msg_data = self.connection.fetch(msg_id, "(RFC822)")
        if status != "OK":
            return None

        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Dekodowanie pól
        date = email_message.get("Date")
        subject = self._decode_header(email_message.get("Subject"))
        message_id = email_message.get("Message-ID")
        content = ""

        # Pobranie treści wiadomości
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                    break
        else:
            content = email_message.get_payload(decode=True).decode(email_message.get_content_charset() or "utf-8")

        return {
            "date": date,
            "subject": subject,
            "content": content,
            "message_id": message_id
        }

    def get_folders(self) -> List[str]:
        """
        Pobiera listę folderów (mailboxów) z serwera IMAP.
        """
        self.check_connection()

        if(self.mailboxes):
            return self.mailboxes

        status, folders = self.connection.list()
        if status != "OK":
            return []

        folder_list = []
        for folder in folders:
            # Foldery są zwracane w formacie b'(flags) "delimiter" folder_name'
            parts = folder.decode().split(' ')
            folder_name = parts[-1].strip('"')
            folder_list.append(folder_name)

        if(not self.mailboxes):
            self.mailboxes = folder_list

        return folder_list
