# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-16 19:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tonerecorder', '0012_auto_20160816_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordedsyllable',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
