# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing', '0001_initial'),
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billinginfo',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directory.Company'),
        ),
        migrations.AddField(
            model_name='bill',
            name='billingInfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.BillingInfo'),
        ),
        migrations.AddField(
            model_name='bill',
            name='cpm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.CPMPrice'),
        ),
    ]
