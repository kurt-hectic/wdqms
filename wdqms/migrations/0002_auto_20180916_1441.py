# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-16 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wdqms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='iso3',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
