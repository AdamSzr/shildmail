
from django.http import HttpRequest
from shildmail.imap.email import Email
from shildmail.imap.manager import imap_manager
from datetime import datetime


class HomePageProps:
    def __init__(self, request):
        self.email = request.user.email
        self.message_id= request.GET.get('message_id')
        self.mailbox = request.GET.get('mailbox', 'INBOX')
        adapter = imap_manager.get_connection(request.user.email)


        if(not adapter):
            raise Exception('No imap connection in manager')

        self.mailboxes = adapter.get_mailboxes()

        selected_mailbox_result = adapter.select_mailbox(self.mailbox)

        self.message_ids = []

        if(selected_mailbox_result):
           self.message_ids = adapter.get_message_ids()

        self.selected_message = None

        if selected_mailbox_result:
            self.messages = adapter.get_messages_for(self.mailbox)

        if self.message_id:
            self.selected_message = adapter.get_message(self.message_id)


    def to_dict(self):
        return {
            'email': self.email,
            'mailboxes': self.mailboxes,
            'message_ids': self.message_ids,
            'messages': {key: value.to_dict() for key, value in self.messages.items()},

            'selected_mailbox':self.mailbox,
            'selected_message': self.selected_message.to_dict() if self.selected_message else None,
        }

    def mock(self,request:HttpRequest):
        message_id= request.GET.get('message_id')
        mailbox = request.GET.get('mailbox')

        print(f'{message_id} | {mailbox}')


        messages = {
                '1': Email().to_dict(),
                '2': Email().to_dict(),
                '3': Email().to_dict(),
                '4': Email().to_dict(),
        }

        return {
            'email':'simple@adamszreiber.pl',
            'mailboxes':['INBOX','Trash','Sent'],
            'message_ids':['1','2','3','4'],
            'selected_mailbox':mailbox,
            'selected_message': messages[message_id] if message_id is not None else None,
            'messages':messages
        }
