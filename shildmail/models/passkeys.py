from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from user import User

class PasskeyManager(models.Manager):
    def by_user_email(self, email):
        """Zwraca wszystkie passkeys przypisane do użytkownika o podanym adresie e-mail."""
        return self.filter(user_email=email)

    def active_passkeys(self):
        """Zwraca wszystkie aktywne passkeys, czyli te z niezerowym licznikiem."""
        return self.filter(counter__gt=0)

    def backup_eligible(self):
        """Zwraca wszystkie passkeys, które są kwalifikowane do kopii zapasowych."""
        return self.filter(backup_eligible=True)

    def recently_used(self, days=30):
        """Zwraca passkeys używane w ciągu ostatnich `days` dni."""
        cutoff_date = now() - timedelta(days=days)
        return self.filter(last_used__gte=cutoff_date)


class Passkey(models.Model):
    cred_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Base64url string"
    )
    cred_public_key = models.BinaryField()
    user_email = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="passkeys",
        help_text="User's email address"
    )
    webauthn_user_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Base64url string; userHandle during authentication"
    )
    counter = models.PositiveIntegerField()
    backup_eligible = models.BooleanField()
    backup_status = models.BooleanField()
    transports = models.TextField(
        blank=True,
        help_text="Comma-separated values for transports"
    )
    created_at = models.DateTimeField(default=now)
    last_used = models.DateTimeField(null=True, blank=True)

    # Dodanie niestandardowego menedżera
    objects = PasskeyManager()

    class Meta:
        db_table = 'passkeys'  # Zmieniona nazwa tabeli
        verbose_name = "Klucz uwierzytelniający"
        verbose_name_plural = "Klucze uwierzytelniające"

    def __str__(self):
        return f"Passkey for {self.user_email} (cred_id={self.cred_id})"
