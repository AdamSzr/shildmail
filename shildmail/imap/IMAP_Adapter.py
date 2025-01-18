from imaplib import IMAP4_SSL
import email
from typing import List, Dict, Optional
from logging import LoggerAdapter, getLogger, StreamHandler, Formatter,DEBUG
from shildmail.imap.email import Email
from shildmail.settings import IMAP_HOST, IMAPS_PORT

logger = getLogger()
logger.setLevel(DEBUG)

handler = StreamHandler()
formatter = Formatter('[%(asctime)s] IMAPAdapter %(message)s',  datefmt='%d/%b/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

class IMAPAdapter:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.connection: IMAP4_SSL | None = None
        self.mailbox: str | None = None

        self.storage = Message_Storage()


    def connect(self):
        """
        Łączy się z serwerem IMAP i loguje.
        """
        logger.info(f"Creating connection")
        self.connection = IMAP4_SSL(IMAP_HOST, IMAPS_PORT)
        self.connection.login(self.username, self.password)

    def disconnect(self):
        """
        Zamyka połączenie z serwerem IMAP.
        """
        if self.connection:
            if(self.connection.state == 'SELECTED'):
               self.connection.close()

            self.connection.logout()
            self.connection = None

            logger.info(f"Bye bye")

    def check_connection(self):
        if not self.connection:
            raise RuntimeError("Not connected to IMAP server.")

    def get_mailboxes(self) -> List[str]:
        """
        Pobiera listę folderów (mailboxów) z serwera IMAP.
        """
        self.check_connection()

        mailboxes = self.storage.get_mailboxes()

        if(mailboxes): return mailboxes

        folder_list = []
        status, folders = self.connection.list()
        logger.info('Fetching mailboxes')

        if not status == 'OK':
            return folder_list

        for folder in folders:
            # Foldery są zwracane w formacie b'(flags) "delimiter" folder_name'
            parts = folder.decode().split(' ')
            folder_name = parts[-1].strip('"')
            folder_list.append(folder_name)

        mailboxes = sorted(folder_list, key=lambda x: (x != "INBOX", x))

        self.storage.add_mailboxes(mailboxes)

        return mailboxes

    def select_mailbox(self,mailbox:str):
        if(not self.storage.mailbox_exists(mailbox)):
            raise Exception('First run get_folders function')

        if self.mailbox == mailbox:
            return True

        status, data= self.connection.select(mailbox)
        success = (status == 'OK')

        logger.info(f"Selecting {mailbox}")

        if success:
            self.mailbox = mailbox

        self.storage.add_mailbox(mailbox)

        return success

    def get_message_ids(self):
        if not self.mailbox:
             raise Exception('First run select the mailbox')

        messages_ids = self.storage.get_message_ids(self.mailbox)

        if messages_ids: return messages_ids

        status, data = self.connection.search(None,'ALL')
        logger.info(f"{self.mailbox} - Fetching messages_ids")

        if not status == 'OK':
            raise Exception('failed during loading messages_ids')

        mess_ids = data[0].decode('utf-8').split()

        self.storage.add_message_ids( self.mailbox, mess_ids )

        return mess_ids


    def get_message(self, message_id: str) -> Email:
        """Pobieranie treści wiadomości na podstawie message_id"""
        # Sprawdzenie, czy wiadomość już została pobrana
        mess = self.storage.get_message(self.mailbox, message_id)
        if mess: return mess

        # Pobieranie wiadomości
        status, data = self.connection.fetch(message_id, "(RFC822)")

        logger.info(f"Fetching message: {message_id}")
        if not status == 'OK':
            raise Exception(f"Nie udało się pobrać wiadomości o ID: {message_id}")

        for response_part in data:
            if isinstance(response_part, tuple):
                # Parsowanie wiadomości i tworzenie obiektu Email
                raw_msg = email.message_from_bytes(response_part[1])
                email_obj = Email(raw_msg)

                # Przechowywanie wiadomości w słowniku
                self.storage.set_message(self.mailbox,message_id,email_obj)

                return email_obj


    def get_messages_for(self, mailbox:str) -> List[Email]:
        if  not self.storage.mailbox_exists(mailbox):
            raise Exception(f'Invalid mailbox [{mailbox}]', self.mailboxes)

        message_ids = self.storage.get_message_ids(mailbox)

        mails = {}

        for message_id in message_ids:
            mails[message_id] = self.get_message(message_id)

        return mails


    def get_messages(self, message_ids: list[str]) -> Dict[str, Email]:
        """
        Pobiera wiadomości dla listy message_ids i zwraca słownik z message_id jako kluczami i obiektami Email jako wartościami.
        """

        # Przechodzimy przez listę identyfikatorów wiadomości
        for message_id in message_ids:
            try:
                # Pobieramy wiadomość za pomocą istniejącej metody
                self.get_message(message_id)
            except Exception as e:
                # Obsługuje błąd, jeśli wiadomości nie uda się pobrać
                print(f"Błąd podczas pobierania wiadomości {message_id}: {e}")

        return self.messages


class Message_Storage:
    def __init__(self):
        self.messages_storage: Dict[str, Dict[str, Email]] = {}

    def get_mailboxes(self) -> List[str] | None:
        if len(self.messages_storage.keys()) > 0:
            return list(self.messages_storage.keys())
        return None

    def get_message_ids(self, mailbox):
        if self.mailbox_exists(mailbox): return list(self.messages_storage[mailbox].keys())
        else: return None

    def get_message(self, mailbox, message_id: str):
        if(self.mailbox_exists(mailbox)): return self.messages_storage[mailbox][message_id]
        else: return None

    def get_messages_for(self, mailbox:str):
        if(not self.mailbox_exists()): return None

        return list(self.messages_storage[mailbox].values())

    def add_mailboxes(self, mailboxes: List[str]):
        for mailbox in mailboxes:
            self.add_mailbox(mailbox)

    def mailbox_exists(self, mailbox:str):
        return mailbox in self.messages_storage

    def add_mailbox(self, mailbox:str):
        if(not self.mailbox_exists(mailbox)):
             self.messages_storage[mailbox] = {}

    def add_message_ids(self, mailbox:str, message_id:str):
        for id in message_id:
            self.add_message_id(mailbox, id)

    def add_message_id(self, mailbox:str, message_id:str):
        self.add_mailbox(mailbox)

        self.messages_storage[mailbox][message_id] = None

    def set_message(self, mailbox:str, id:str, message:Email):
        self.add_mailbox(mailbox)

        self.messages_storage[mailbox][id] = message
