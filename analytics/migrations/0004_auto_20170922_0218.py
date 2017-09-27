# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-22 02:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_auto_20170919_1848'),
        ('directory', '0003_auto_20170921_2222'),
        ('analytics', '0003_auto_20170919_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillboardReferral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referrer', models.CharField(max_length=2083, null=True)),
                ('dateTime', models.DateTimeField(auto_now=True)),
                ('remoteHost', models.CharField(max_length=150, null=True)),
                ('remoteIP', models.CharField(max_length=150, null=True)),
                ('userAgent', models.CharField(max_length=200, null=True)),
                ('language', models.CharField(max_length=1000, null=True)),
                ('interaction', models.CharField(max_length=100)),
                ('billboardMedia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaigns.BillboardMedia')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directory.Company')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directory.Employee')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='billboard',
            name='target',
        ),
    ]