# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-28 20:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tonerecorder', '0013_auto_20160816_1924'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recordedsyllable',
            unique_together=set([]),
        ),
    ]
