# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from directory.models import Company

class BillingInfo(models.Model):
    company = models.ForeignKey(Company)
    deleted = models.BooleanField(default=False)
    stripeCustomer = models.CharField(max_length=1500)
class CPMPrice(models.Model):
    startDate = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)
class Bill(models.Model):
    billingInfo = models.ForeignKey(BillingInfo)
    displayCount = models.IntegerField(default=0)
    cpm = models.ForeignKey(CPMPrice)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)#prices in USD... stripe does conversion

class Payment(models.Model):
    bill = models.ForeignKey(Bill)
    stripeCharge = models.CharField(max_length=1500)
