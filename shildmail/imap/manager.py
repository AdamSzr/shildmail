import imaplib
import logging
from typing import Dict, Optional
from shildmail.imap.IMAP_Adapter import IMAPAdapter

# Konfiguracja loggera
logger = logging.getLogger('[IMAP Manager]')

class IMAPManager:
    def __init__(self):
        # Słownik do przechowywania połączeń IMAP dla użytkowników
        self.connections: Dict[str,IMAPAdapter] = {}

    def get_connection(self, email: str) -> Optional[IMAPAdapter]:
        """
        Zwraca połączenie IMAP dla podanego user_id, lub None, jeśli nie ma połączenia.
        """
        print(list(self.connections.keys()))
        return self.connections.get(email)

    def create_connection(self, email: str, password: str) -> IMAPAdapter:
        """
        Tworzy nowe połączenie IMAP i przechowuje je w słowniku.
        """
        if email in self.connections:
            logger.warning(f"Połączenie IMAP już istnieje dla użytkownika {email}")
            return self.connections[email]

        try:
            # Tworzenie połączenia IMAP
            connection = IMAPAdapter(username=email,password=password)
            connection.connect()

            self.connections[email] = connection
            logger.info(f"Połączenie IMAP utworzone dla użytkownika {email}")
            return connection
        except Exception as e:
            logger.error(f"Nie udało się utworzyć połączenia IMAP dla użytkownika {email}: {e}")
            raise

    def close_connection(self, email: str):
        """
        Zamyka połączenie IMAP dla użytkownika.
        """
        connection = self.connections.pop(email, None)
        if connection:
            try:
                connection.disconnect()
                logger.info(f"Połączenie IMAP zamknięte dla użytkownika {email}")
            except Exception as e:
                logger.error(f"Nie udało się zamknąć połączenia IMAP dla użytkownika {email}: {e}")
        else:
            logger.warning(f"Połączenie IMAP nie znaleziono dla użytkownika {email}")

    def list_connections(self):
        """
        Zwraca listę wszystkich aktywnych połączeń IMAP.
        """
        return list(self.connections.keys())

    def delete_connection(self, email: str):
        """
        Usuwa połączenie IMAP dla użytkownika.
        """
        if email in self.connections:
            self.close_connection(email)
            logger.info(f"Połączenie IMAP usunięte dla użytkownika {email}")
        else:
            logger.warning(f"Połączenie IMAP nie znaleziono dla użytkownika {email}")


imap_manager = IMAPManager()