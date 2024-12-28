from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomEmailBackend(BaseBackend):
    """
    Niestandardowy backend uwierzytelniania na podstawie adresu email i hasła.
    """

    def authenticate(self, request, email=None, password=None):
        # print(email, password)
        try:
            # Znajdź użytkownika na podstawie emaila
            user = User.objects.get(pk=email)
        except User.DoesNotExist:
            return None

        # Sprawdź hasło
        if user.check_password(password) :
            return user

        return None

    def get_user(self, email):
        try:
            return User.objects.get(pk=email)
        except User.DoesNotExist:
            return None
