import imaplib
import logging
from typing import Optional

# Konfiguracja loggera
logger = logging.getLogger('[IMAP Manager]')

class IMAPManager:
    def __init__(self):
        # Słownik do przechowywania połączeń IMAP dla użytkowników
        self.connections = {}

    def get_connection(self, user_id: str) -> Optional[imaplib.IMAP4_SSL]:
        """
        Zwraca połączenie IMAP dla podanego user_id, lub None, jeśli nie ma połączenia.
        """
        return self.connections.get(user_id)

    def create_connection(self, user_id: str, email: str, password: str, imap_server: str = 'mail.adamszreiber.pl') -> imaplib.IMAP4_SSL:
        """
        Tworzy nowe połączenie IMAP i przechowuje je w słowniku.
        """
        if user_id in self.connections:
            logger.warning(f"Połączenie IMAP już istnieje dla użytkownika {user_id}")
            return self.connections[user_id]

        try:
            # Tworzenie połączenia IMAP
            connection = imaplib.IMAP4_SSL(imap_server)
            connection.login(email, password)
            self.connections[user_id] = connection
            logger.info(f"Połączenie IMAP utworzone dla użytkownika {user_id}")
            return connection
        except Exception as e:
            logger.error(f"Nie udało się utworzyć połączenia IMAP dla użytkownika {user_id}: {e}")
            raise

    def close_connection(self, user_id: str):
        """
        Zamyka połączenie IMAP dla użytkownika.
        """
        connection = self.connections.pop(user_id, None)
        if connection:
            try:
                connection.logout()
                logger.info(f"Połączenie IMAP zamknięte dla użytkownika {user_id}")
            except Exception as e:
                logger.error(f"Nie udało się zamknąć połączenia IMAP dla użytkownika {user_id}: {e}")
        else:
            logger.warning(f"Połączenie IMAP nie znaleziono dla użytkownika {user_id}")

    def list_connections(self):
        """
        Zwraca listę wszystkich aktywnych połączeń IMAP.
        """
        return list(self.connections.keys())

    def delete_connection(self, user_id: str):
        """
        Usuwa połączenie IMAP dla użytkownika.
        """
        if user_id in self.connections:
            self.close_connection(user_id)
            logger.info(f"Połączenie IMAP usunięte dla użytkownika {user_id}")
        else:
            logger.warning(f"Połączenie IMAP nie znaleziono dla użytkownika {user_id}")


imap_manager = IMAPManager()