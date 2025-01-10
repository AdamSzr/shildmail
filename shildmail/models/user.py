from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, realname=None, **extra_fields):
         # Sprawdzamy, czy email i realname są obecne
        if not email:
            raise ValueError("The Email field must be set")
        if not realname:
            raise ValueError("The Realname field must be set")

        # Normalizowanie emaila (np. zmiana na małe litery)
        # Tworzenie instancji użytkownika
        user = self.model(email=email, realname=realname, **extra_fields)

        # Automatyczna generacja `mail_dir` na podstawie `realname`
        user.password = "{PLAIN}" + password
        user.mail_dir = realname.lower().replace(' ', '_')

        # Zapisujemy użytkownika
        user.save(using=self._db)

    # def get(self,*args, **kwargs):
    #     return super().get(*args, **kwargs)



class User(AbstractBaseUser):
    email = models.EmailField(unique=True, primary_key=True, max_length=255)
    realname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    maildir = models.CharField(max_length=255, editable=False)  # Pole tylko do odczytu w formularzach
    # required by django
    # last_login = models.DateTimeField(_("last login"), blank=True, null=True)
    # is_active = True

    objects = UserManager()  # Przypisanie menedżera do modelu

    USERNAME_FIELD='email'

    class Meta:
        db_table = 'users'  # Zmieniona nazwa tabeli
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def check_password(self,passw):
       return  self.password == passw

    def to_dict(self):
        return {'email':self.email, 'realname':self.realname, 'password':self.password }

    def __str__(self):
        return self.email

