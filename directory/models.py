# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User as Django_User
import xxhash,random
# Create your models here.
class Company(models.Model):
    domain = models.CharField(max_length=150,unique=True)
    name = models.CharField(max_length=150)
class User(Django_User):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    timezone = models.CharField(max_length=200, default='US/Eastern')
    class Meta:
        permissions = (
            ("full_user", "Can CRUD other full users."),
            ("half_user", "Can CRUD itself."),
        )
class Group(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    class Meta:
        unique_together = (("company","name"),)
class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True)
    first = models.CharField(max_length=150)
    last = models.CharField(max_length=150)
    dept = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254)
    url = models.CharField(max_length=2500, unique=True)#random for safety)
    class Meta:
        unique_together = (("email","company"),)
