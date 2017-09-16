# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from directory.models import Group,Company
# Create your models here.
class Billboard(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group,blank=True)#campaigns applied by smallest group, then most recent
    name = models.CharField(max_length=150)
    targeturl = models.CharField(max_length=2083)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(null=True)#null is it doesn't end.
class Photo(models.Model):#allows for varied media for future ab testing
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    imgurDeleteHash = models.CharField(max_length=2083)
    imgurId = models.CharField(max_length=2083)
    imgurLink = models.CharField(max_length=2083)

class BillboardMedia(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    billboard = models.ForeignKey(Billboard, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    on = models.BooleanField(default=True)
