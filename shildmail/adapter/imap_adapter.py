
import re


# class ImapAdapter:


#     def directories(self,connection):
#         status, folders = connection.list()

#         if status != 'OK':
#             return None

#         regex = re.compile(r'\(.+\) "." (?P<dir_name>\w+)')

#         # Wyciągnięcie `dir_name` z każdego wpisu
#         dir_names = [match.group('dir_name') for folder in folders if (match := regex.search(folder.decode()))]

#         return dir_names

#     def select(self, directory):
#         # Wybór folderu INBOX
#         status, response = mail.select("INBOX")
#         if status == 'OK':
#             print("Folder INBOX został otwarty.")
#         else:
#             print(f"Nie udało się otworzyć folderu INBOX: {response}")


class ImapAdapter:
    def __init__(self, imap_client):
        """
        Konstruktor klasy ImapAdapter.

        :param imap_client: Instancja obiektu ImapClient
        """
        self.imap_client = imap_client
        self.current_directory = None
        self.cached_directories = None

    def list_directories(self):
        """
        Pobiera listę katalogów z serwera IMAP i je przechowuje w pamięci podręcznej.

        :return: Lista nazw katalogów
        """
        if self.cached_directories is None:
            self.cached_directories = self.imap_client.list_folders()
        return [dir_info[-1] for dir_info in self.cached_directories]

    def select(self, directory):
        """
        Wybiera katalog na serwerze IMAP.

        :param directory: Nazwa katalogu
        """
        status, _ = self.imap_client.select_folder(directory)
        if status == 'OK':
            self.current_directory = directory
        else:
            raise Exception(f"Nie udało się wybrać katalogu: {directory}")

    def load_headers(self):
        """
        Pobiera nagłówki wiadomości z aktualnie wybranego katalogu.

        :return: Lista nagłówków wiadomości
        """
        if not self.current_directory:
            raise Exception("Nie wybrano katalogu. Użyj metody select().")

        status, message_ids = self.imap_client.search(None, 'ALL')
        if status != 'OK':
            raise Exception("Nie udało się pobrać identyfikatorów wiadomości.")

        headers = []
        for msg_id in message_ids[0].split():
            status, msg_data = self.imap_client.fetch(msg_id, '(BODY[HEADER])')
            if status == 'OK':
                headers.append(msg_data)

        return headers

    def load_message(self, msg_id):
        """
        Pobiera pełną wiadomość na podstawie jej identyfikatora.

        :param msg_id: Identyfikator wiadomości
        :return: Treść wiadomości
        """
        if not self.current_directory:
            raise Exception("Nie wybrano katalogu. Użyj metody select().")

        status, msg_data = self.imap_client.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            raise Exception(f"Nie udało się pobrać wiadomości o ID: {msg_id}")

        return msg_data[0][1]
