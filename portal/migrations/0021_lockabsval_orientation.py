# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-29 16:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0020_auto_20160807_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockabsval',
            name='orientation',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]
