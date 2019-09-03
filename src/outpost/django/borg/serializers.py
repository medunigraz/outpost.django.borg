from rest_framework import serializers

from . import models


class RepositorySerializer(serializers.ModelSerializer):
    path = serializers.CharField()

    class Meta:
        model = models.Repository
        fields = ("name", "openssh", "path")


class ServerSerializer(serializers.ModelSerializer):
    repositories = RepositorySerializer(source="repository_set.all", many=True)

    class Meta:
        model = models.Server
        fields = ("name", "openssh", "username", "repositories", "path")
