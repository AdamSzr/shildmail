from imaplib import IMAP4_SSL
import email
from typing import List, Dict, Optional

from shildmail.imap.email import Email
from shildmail.settings import IMAP_HOST, IMAPS_PORT

class IMAPAdapter:
    def __init__(self, username: str, password: str):
        self.username = username
        self.email = username
        self.password = password
        self.raw_password = password.replace('{PLAIN}','')
        self.connection: IMAP4_SSL | None = None
        self.mailbox: str | None = None

        self.mailboxes: List[str] | None = None
        self.messages_ids: Dict[ str, List[str]] = {}
        self.messages: Dict[str, Email] = {}


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

    def select_mailbox(self,mailbox:str):
        if(not self.mailboxes):
            raise Exception('First run get_folders function')

        if mailbox not in self.mailboxes:
            return False

        if self.mailbox == mailbox:
            return True

        status, data= self.connection.select(mailbox)
        success = (status == 'OK')

        if success:
            self.mailbox = mailbox

        return success

    def get_message_ids(self):
        if not self.mailbox:
             raise Exception('First run select the mailbox')

        if self.mailbox in self.messages_ids:
            return self.messages_ids[self.mailbox]

        status, data = self.connection.search(None,'ALL')
        if not status == 'OK':
            raise Exception('failed during loading messages_ids')

        mess_ids = data[0].decode('utf-8').split()
        self.messages_ids[self.mailbox] = mess_ids
        return mess_ids

    def get_messages_for(self, mailbox:str) -> List[Email]:
        if mailbox not in self.mailboxes:
            raise Exception(f'Invalid mailbox [{mailbox}]', self.mailboxes)
          # Pobieramy listę message_id z danego folderu
        message_ids = self.messages_ids[mailbox]
        
        # Tworzymy listę obiektów Email dla danej listy message_id
        emails = [self.messages[message_id] for message_id in message_ids if message_id in self.messages]
        
        return emails

    def get_message(self, message_id: str) -> Email:
        """Pobieranie treści wiadomości na podstawie message_id"""
        # Sprawdzenie, czy wiadomość już została pobrana
        if message_id in self.messages:
            return self.messages[message_id]

        # Pobieranie wiadomości
        status, data = self.connection.fetch(message_id, "(RFC822)")

        if not status == 'OK':
            raise Exception(f"Nie udało się pobrać wiadomości o ID: {message_id}")
        
        for response_part in data:
            if isinstance(response_part, tuple):
                # Parsowanie wiadomości i tworzenie obiektu Email
                raw_msg = email.message_from_bytes(response_part[1])
                email_obj = Email(raw_msg)

                # Przechowywanie wiadomości w słowniku
                self.messages[message_id] = email_obj

                return email_obj

    def get_mailboxes(self) -> List[str]:
        """
        Pobiera listę folderów (mailboxów) z serwera IMAP.
        """
        self.check_connection()

        if(self.mailboxes):
            return self.mailboxes

        folder_list = []
        status, folders = self.connection.list()

        if not status == 'OK':
            return folder_list

        for folder in folders:
            # Foldery są zwracane w formacie b'(flags) "delimiter" folder_name'
            parts = folder.decode().split(' ')
            folder_name = parts[-1].strip('"')
            folder_list.append(folder_name)

        self.mailboxes = folder_list

        return folder_list
