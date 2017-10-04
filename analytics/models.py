# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from directory.models import Employee, Company, User
from campaigns import models as billboard_models
from datetime import datetime

class Event(models.Model):
    company = models.ForeignKey(Company)
    referrer = models.CharField(null=True, max_length=2083)
    dateTime = models.DateTimeField(auto_now=True)
    remoteHost = models.CharField(null=True,max_length=150)
    remoteIP = models.CharField(null=True,max_length=150)
    userAgent = models.CharField(null=True,max_length=200)
    language = models.CharField(null=True,max_length=1000)
    class Meta:
        abstract=True
class OnsiteEvent(models.Model):
    page = models.CharField(null=True,max_length=2083)
    class Meta:
        abstract=True
#FOR CUSTOMERS/COMPANIES
class Billboard(Event):
    interaction = models.CharField(max_length=100)#click or display
    billboardMedia = models.ForeignKey(billboard_models.BillboardMedia,related_name="creative")
    employee = models.ForeignKey(Employee)
class BillboardReferral(Event):#Creates a proprietary referral chain
    interaction = models.CharField(max_length=100)
    #space for special robinboard referral image
    # ref = models.ForeignKey(ProprietaryReferral,null=True,default=None)#eventual proprietary referral created if
#INTERNAL
class ReferralChain(models.Model):#set cookie from this, original gets the cookie, maybe up to 30 days? attach the conversion here.
    successful_chain=models.ForeignKey("self",null=True,default=None)
    #every new visitor gets a referral chain..detect referral chain for logged in user, break it, associate it with successful chain?
class PageView(OnsiteEvent):
    chain = models.ForeignKey(ReferralChain)
class Referral(OnsiteEvent):
    chain = models.ForeignKey(ReferralChain)
    source = models.CharField(max_length=300)#location: forward, facebook, twittter, copy/paste
    # target = models.CharField(max_length=500)#Company or EmployeeOnboard...decode from the page
    class Meta:
        abstract=True

class EmployeeReferral(Referral):#referral of employee to join company's robinboard
    employee = models.ForeignKey(Employee,null=True)
class UserReferral(Referral):
    user = models.ForeignKey(User,null=True)
    #need new employee result
class ProprietaryReferral(Referral):#referral by robinboard strategy...used to be able to track different bonus strategy promotions
    pass
class Conversion(models.Model):
    dateTime = models.DateTimeField(auto_now=True)
    chain = models.ForeignKey(ReferralChain)
    class Meta:
        abstract = True
class EmployeeOnboard(Conversion):
    new_employee = models.ForeignKey(Employee)#new employee
class CompanyOnboard(Conversion):#referral
    new_company = models.ForeignKey(Company)#new company
