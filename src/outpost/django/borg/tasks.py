import io
import asyncssh
import asyncio
import logging
from datetime import timedelta

import requests
from celery.task import PeriodicTask

from .conf import settings
from .models import Server

logger = logging.getLogger(__name__)


class BorgStatusTask(PeriodicTask):
    run_every = timedelta(minutes=30)

    def run(self, **kwargs):
        for server in Server.objects.filter(enabled=True):
            try:
                result = asyncio.run(self.stats(server))
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

    async def stats(self, server):
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
