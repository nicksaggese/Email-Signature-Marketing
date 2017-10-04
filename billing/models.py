# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from directory.models import Company
from analytics.models import CompanyOnboard
class BillingInfo(models.Model):
    company = models.ForeignKey(Company)
    stripeCustomer = models.CharField(max_length=1500)
    budget = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)#prices in USD... stripe does conversion
    dateTime = models.DateTimeField(auto_now=True)
class Price(models.Model):#historical pricing, per click
    startDate = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)
    credits = models.IntegerField(default=1)

class referBonus(models.Model):
    startDate = models.DateTimeField(auto_now=True)
    give_credits = models.IntegerField(default=1)
    take_credits = models.IntegerField(default=1)
    renew_monthly = models.BooleanField(default=False)#non permanent credits

class Credit(models.Model):#these are assessed via daily script
    company = models.ForeignKey(Company)
    onboard = models.ForeignKey(CompanyOnboard)
    referBonus = models.ForeignKey(referBonus)
    isGive = models.BooleanField(default=True)#false indicates take
    credits = models.IntegerField(default=1)#could be no credits to indicate a scenario where credits are unavailable

class Bill(models.Model):
    billingInfo = models.ForeignKey(BillingInfo)
    debits = models.IntegerField(default=1)#how many credits used this cycle
    pricepoint = models.ForeignKey(Price)#dynamically calculate price off of debits
    # total = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)#prices in USD... stripe does conversion

class Payment(models.Model):
    bill = models.ForeignKey(Bill)
    debits = models.IntegerField(default=1)
class StripePayment(Payment):
    stripeCharge = models.CharField(max_length=1500)
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=2.00)
class CreditPayment(Payment):
    used = models.ManyToManyField(Credit)
