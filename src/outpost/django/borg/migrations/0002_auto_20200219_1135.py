# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-19 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("borg", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="repository",
            name="append_only",
            field=models.BooleanField(default=False, help_text=""),
        )
    ]
