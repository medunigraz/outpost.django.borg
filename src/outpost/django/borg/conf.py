import os

from appconf import AppConf
from django.conf import settings


class BorgAppConf(AppConf):
    SSH_KEY_ALGORITHM = "ssh-ed25519"
    SECRET_LENGTH = 32
    RATIO_PRECISION = 2
    REPOSITORY_DIRECTORY = "repos"

    class Meta:
        prefix = "borg"
