# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-21 17:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_counterglobal'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CounterGlobal',
            new_name='counter',
        ),
    ]