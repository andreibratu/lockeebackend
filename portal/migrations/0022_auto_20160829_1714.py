# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-29 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0021_lockabsval_orientation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockabsval',
            name='orientation',
            field=models.CharField(default='left', max_length=10),
        ),
    ]
