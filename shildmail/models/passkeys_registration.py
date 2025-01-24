import time

class PasskeysRegistration:
    def __init__(self, id:str, email:str):
        self.id = id
        self.email = email
        self.challange = None
        self.created_at = time.time()

    def is_expired(self):
        return time.time() - self.created_at >= 60