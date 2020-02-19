import secrets
import string
from base64 import b64encode
from hashlib import sha256
from pathlib import Path

import asyncssh
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from django.utils.deconstruct import deconstructible
from django.core.validators import RegexValidator
from django_extensions.db.models import TimeStampedModel

from outpost.django.base.decorators import signal_connect
from outpost.django.base.validators import PublicKeyValidator, PrivateKeyValidator
from outpost.django.campusonline.models import Person, Student


from .conf import settings


class Server(models.Model):
    def generate_private_key():
        key = asyncssh.generate_private_key(settings.BORG_SSH_KEY_ALGORITHM)
        return key.export_private_key("openssh")

    name = models.CharField(max_length=128)
    host = models.ForeignKey("salt.Host", related_name="borg")
    enabled = models.BooleanField(default=False)
    username = models.CharField(max_length=128, default="borg")
    path = models.CharField(max_length=128, default="/var/lib/borg")
    private_key = models.TextField(
        validators=(PrivateKeyValidator(),), default=generate_private_key
    )
    host_key = models.TextField(validators=(PublicKeyValidator(),))
    size = models.BigIntegerField(default=0)
    used = models.BigIntegerField(default=0)

    class Meta:
        unique_together = (("username", "path", "host"),)

    def __str__(self):
        return self.name

    @property
    def fingerprint(self):
        k = asyncssh.import_private_key(self.private_key)
        d = sha256(k.get_ssh_public_key()).digest()
        f = b64encode(d).replace(b"=", b"").decode("utf-8")
        return "SHA256:{}".format(f)

    @property
    def openssh(self):
        k = asyncssh.import_private_key(self.private_key)
        return k.export_public_key()

    @property
    def used_ratio(self):
        if self.size == 0:
            return 0
        return (self.used / self.size) * 100

    @property
    def repository(self):
        return Path(self.path).joinpath(settings.BORG_REPOSITORY_DIRECTORY).as_posix()


class Repository(TimeStampedModel):
    def generate_secret():
        length = settings.BORG_SECRET_LENGTH
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(length))

    server = models.ForeignKey("Server")
    name = models.CharField(
        max_length=128,
        validators=(
            RegexValidator(r"^[A-Za-z0-9_]+$", message=_("Invalid name for directory")),
        ),
    )
    secret = models.CharField(
        max_length=settings.BORG_SECRET_LENGTH, default=generate_secret, unique=True
    )
    append_only = models.BooleanField(default=False, help_text=_(""))
    public_key = models.TextField(validators=(PublicKeyValidator(),))
    updated = models.DateTimeField(blank=True, null=True)
    raw = models.BigIntegerField(default=0)
    compressed = models.BigIntegerField(default=0)
    deduplicated = models.BigIntegerField(default=0)

    class Meta:
        unique_together = (("server", "name"),)

    def __str__(self):
        return f"{self.server}:{self.name}"

    @property
    def path(self):
        return (
            Path(self.server.path)
            .joinpath(settings.BORG_REPOSITORY_DIRECTORY)
            .joinpath(self.name)
            .as_posix()
        )

    @property
    def fingerprint(self):
        k = asyncssh.import_public_key(self.public_key)
        d = sha256(k.get_ssh_public_key()).digest()
        f = b64encode(d).replace(b"=", b"").decode("utf-8")
        return "SHA256:{}".format(f)

    @property
    def openssh(self):
        k = asyncssh.import_public_key(self.public_key)
        return k.export_public_key()

    @property
    def comment(self):
        k = asyncssh.import_public_key(self.public_key)
        return k.get_comment()

    @property
    def compression_ratio(self):
        if self.compressed == 0:
            return 0
        return (1 - (self.compressed / self.raw)) * 100

    @property
    def deduplication_ratio(self):
        if self.deduplicated == 0:
            return 0
        return (1 - (self.deduplicated / self.compressed)) * 100


class Archive(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    repository = models.ForeignKey("Repository")
    name = models.CharField(max_length=128)
    start = models.DateTimeField()
    end = models.DateTimeField()
    files = models.BigIntegerField(default=0)
    raw = models.BigIntegerField(default=0)
    compressed = models.BigIntegerField(default=0)
    deduplicated = models.BigIntegerField(default=0)

    class Meta:
        ordering = ("start", "end")

    def __str__(self):
        return self.name

    @property
    def compression_ratio(self):
        if self.compressed == 0:
            return 0
        return (1 - (self.compressed / self.raw)) * 100

    @property
    def deduplication_ratio(self):
        if self.deduplicated == 0:
            return 0
        return (1 - (self.deduplicated / self.compressed)) * 100

    @property
    def duration(self):
        return str(self.end - self.start)
