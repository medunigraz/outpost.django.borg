import io
import paramiko
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
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.pkey.PKey.from_private_key(
                io.BytesIO(server.private_key)
            )
            try:
                ssh.connect(server.host, username=server.username, pkey=private_key)
            except paramiko.SSHException as e:
                logger.error(f"Could not connect to host {server.host}: {e}")
                ssh.close()
                continue
            inp, out, err = ssh.exec_command(
                f"df --output=file,size,used,avail -B1 {server.path}"
            )
            for line in out:
                if line.startswith(server.path):
                    (_, size, used, avail) = line.split()
                    server.size = int(size)
                    server.used = int(used)
                    server.save()
                    break
            ssh.close()
