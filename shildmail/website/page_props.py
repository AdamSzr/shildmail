
from shildmail.imap.manager import imap_manager

class HomePageProps:
    def __init__(self, request):
        self.email = request.user.email
        adapter = imap_manager.get_connection(request.user.email)

        if(not adapter): raise Exception('No imap connection in manager')

        self.mailboxes = adapter.get_mailboxes()

        selected = adapter.select_mailbox('INBOX')
        self.message_ids = []

        if(selected):
           self.message_ids = adapter.get_message_ids()

        for message_id in self.message_ids:
            adapter.get_message(message_id)

        self.messages = adapter.get_messages_for(adapter.mailbox)

    def to_dict(self):
        return {
            'email': self.email,
            'mailboxes': self.mailboxes,
            'message_ids': self.message_ids,
            'messages': self.messages
        }