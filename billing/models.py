# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from directory.models import Company

class BillingInfo(Company):
    pass

class Bill(models.Model):
    pass

class Payment(models.Model):
    pass
