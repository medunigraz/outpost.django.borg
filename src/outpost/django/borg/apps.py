from django.apps import AppConfig


class BorgConfig(AppConfig):
    name = "outpost.django.borg"

    def ready(self):
        from outpost.django.salt.serializers import HostSerializer
        from .serializers import ServerSerializer

        HostSerializer.Meta.extensions["borg"] = ServerSerializer(
            source="borg.all", many=True
        )
