# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('campaigns', '0001_initial'),
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billboard',
            name='billboardMedia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creative', to='campaigns.BillboardMedia'),
        ),
    ]