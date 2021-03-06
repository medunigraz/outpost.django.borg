# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-18 21:40
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import outpost.django.base.validators
import outpost.django.borg.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("salt", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Archive",
            fields=[
                (
                    "id",
                    models.CharField(max_length=64, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=128)),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField()),
                ("files", models.BigIntegerField(default=0)),
                ("raw", models.BigIntegerField(default=0)),
                ("compressed", models.BigIntegerField(default=0)),
                ("deduplicated", models.BigIntegerField(default=0)),
            ],
            options={"ordering": ("-start", "-end")},
        ),
        migrations.CreateModel(
            name="Repository",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[A-Za-z0-9_]+$", message="Invalid name for directory"
                            )
                        ],
                    ),
                ),
                (
                    "secret",
                    models.CharField(
                        default=outpost.django.borg.models.Repository.generate_secret,
                        editable=False,
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("append_only", models.BooleanField(default=False, help_text="")),
                (
                    "public_key",
                    models.TextField(
                        validators=[outpost.django.base.validators.PublicKeyValidator()]
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                ("raw", models.BigIntegerField(default=0, editable=False)),
                ("compressed", models.BigIntegerField(default=0, editable=False)),
                ("deduplicated", models.BigIntegerField(default=0, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name="Server",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("enabled", models.BooleanField(default=False)),
                ("username", models.CharField(default="borg", max_length=128)),
                ("path", models.CharField(default="/var/lib/borg", max_length=128)),
                (
                    "private_key",
                    models.TextField(
                        default=outpost.django.borg.models.Server.generate_private_key,
                        validators=[
                            outpost.django.base.validators.PrivateKeyValidator()
                        ],
                    ),
                ),
                (
                    "host_key",
                    models.TextField(
                        validators=[outpost.django.base.validators.PublicKeyValidator()]
                    ),
                ),
                ("size", models.BigIntegerField(default=0)),
                ("used", models.BigIntegerField(default=0)),
                (
                    "host",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borg",
                        to="salt.Host",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="repository",
            name="server",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="borg.Server"
            ),
        ),
        migrations.AddField(
            model_name="archive",
            name="repository",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="borg.Repository"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="server", unique_together=set([("username", "path", "host")])
        ),
        migrations.AlterUniqueTogether(
            name="repository", unique_together=set([("server", "name")])
        ),
    ]
