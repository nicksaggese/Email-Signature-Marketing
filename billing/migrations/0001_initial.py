# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayCount', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=2.0, max_digits=100)),
            ],
        ),
        migrations.CreateModel(
            name='BillingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('stripeCustomer', models.CharField(max_length=1500)),
            ],
        ),
        migrations.CreateModel(
            name='CPMPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startDate', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, default=2.0, max_digits=100)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripeCharge', models.CharField(max_length=1500)),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Bill')),
            ],
        ),
    ]
