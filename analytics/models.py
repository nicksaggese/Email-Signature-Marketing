# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from directory.models import Employee
from campaigns import models as billboard_models
from datetime import datetime
class Event(models.Model):
    referrer = models.CharField(null=True, max_length=2083)
    dateTime = models.DateTimeField(auto_now=True)
    remoteHost = models.CharField(null=True,max_length=150)
    remoteIP = models.CharField(null=True,max_length=150)
    userAgent = models.CharField(null=True,max_length=200)
    language = models.CharField(max_length=1000)
    class Meta:
        abstract=True
class Billboard(Event):
    interaction = models.CharField(max_length=100)#click or display
    target = models.CharField(max_length=100)#viral or billboard
    media = models.ForeignKey(billboard_models.Photo, related_name="photo")
    billboard = models.ForeignKey(billboard_models.Billboard)
    employee = models.ForeignKey(Employee)
