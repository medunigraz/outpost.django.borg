import asyncio
import io
import logging
from datetime import timedelta

import asyncssh
import requests
from celery import shared_task
from django.utils.translation import gettext_lazy as _

from .conf import settings
from .models import Server

logger = logging.getLogger(__name__)


class BorgTasks:

    @shared_task(bind=True, ignore_result=True, name=f"{__name__}.Borg:status")
    def status(task):
        for server in Server.objects.filter(enabled=True):
            try:
                result = asyncio.run(BorgTasks.stats(server))
            except asyncssh.Error as e:
                logger.error(f"Could not connect to {server}: {e}")
                continue
            for line in result.splitlines():
                if line.startswith(server.path):
                    (_, size, used, avail) = line.split()
                    server.size = int(size)
                    server.used = int(used)
                    server.save()
                    break

    async def stats(server):
        options = {
            "username": server.username,
            "client_keys": [asyncssh.import_private_key(server.private_key)],
            "known_hosts": [
                [asyncssh.import_public_key(server.host_key)],
                [],
                [],
                [],
                [],
                [],
                [],
            ],
        }
        async with asyncssh.connect(
            f"{server.host.name}.medunigraz.at", **options
        ) as conn:
            result = await conn.run(
                f"df --output=file,size,used,avail -B1 {server.repository}", check=True
            )
            return result.stdout
