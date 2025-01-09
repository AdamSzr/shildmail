from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField
from . import User
import uuid

from django.db.models import F


class WebAuthnCredentialManager(models.Manager):
    def increment_sign_count(self, credential_id):
        """
        Inkrementuje wartość pola sign_count dla poświadczenia o danym credential_id.
        """
        # Zaktualizowanie pola sign_count poprzez inkrementację
        return self.filter(credential_id=credential_id).update(sign_count=F('sign_count') + 1)

    def update_sign_count(self, credential_id, count):
        """
        Ustawia nową wartość pola sign_count dla poświadczenia o danym credential_id.
        """
        # Zaktualizowanie pola sign_count bezpośrednio na podaną wartość
        return self.filter(credential_id=credential_id).update(sign_count=count)


class WebAuthnCredential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255)
    credential_id = models.BinaryField()
    credential_public_key = models.BinaryField()
    credential_type = models.CharField(max_length=255)
    aaguid = models.CharField(max_length=255)
    transports = ArrayField(models.TextField(max_length=255), default=[])
    is_discoverable = models.BooleanField(default=False)
    sign_count = models.IntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)
    authenticator_attachment = models.CharField(max_length=255, blank=True, null=True)
    public_key_algorithm = models.IntegerField()

    # Przypisanie niestandardowego menedżera
    objects = WebAuthnCredentialManager()

    class Meta:
        verbose_name = "WebAuthn Credential"
        verbose_name_plural = "WebAuthn Credentials"
        db_table = 'passkeys'

    def __str__(self):
        return f"Credential for {self.username} (ID: {self.id})"
