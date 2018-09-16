# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-16 11:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(db_column='cc', max_length=3, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('_bounding_box', models.CharField(db_column='extent', max_length=5000)),
                ('vola_code', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('center', models.CharField(max_length=10)),
                ('filetype', models.CharField(max_length=5)),
                ('date', models.DateField(db_column='mydate')),
            ],
            options={
                'db_table': 'period',
                'managed': True,
                'ordering': ['date', 'center', 'filetype'],
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('wigosid', models.CharField(max_length=200)),
                ('iso3', models.CharField(max_length=3)),
                ('region', models.CharField(max_length=200)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('stationtype', models.CharField(max_length=10)),
                ('nrExp0', models.IntegerField()),
                ('nrExp6', models.IntegerField()),
                ('nrExp12', models.IntegerField()),
                ('nrExp18', models.IntegerField()),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
            options={
                'managed': True,
                'db_table': 'station',
            },
        ),
    ]