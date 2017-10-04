# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view,permission_classes

from rest_framework import permissions

from . import models
from . import serializers

# Create your views here.
import stripe, os

from datetime import timedelta

stripe.api_key = os.environ.get('STRIPE_API_KEY')

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

creditQualifier = {
	min_employees: 25,
	min_displays_employee: 100,
	window_to_credit: timedelta(weeks=6)#time to reach these metrics before referral is dead.
}

freeMonthlyCredits = 10

def getBillingDetails(request):
    cid = request.user.user.company.id
    return models.BillingInfo.objects.filter(company=cid,deleted=False)
@api_view(['POST','GET','PUT','DELETE'])
def billingDetails(request):
    if request.method == "POST":
        bi = getBillingDetails(request)
        if(len(bi) >= 1):
            return HttpResponse("Company already has set of billing details.",status=500)

        data = JSONParser().parse(request)#parse incoming data
        response = stripe.Customer.create(
            email = data.get('email'),
            description = request.user.user.company.name + "(" + request.user.user.company.user.domain + ")",
            metadata = {
                "contact_phone" = data.get('phone'),
                "user_edit" = request.user.user.id,
            },
            source = data.get('stripeToken'),
        )
        print response
        # response = JSONParser().parse(response)#parse incoming data
        print response
        try:
            b = models.BillingInfo(company=request.user.user.company.id, stripeCustomer=response.id)
            b.save()
            return HttpResponse(status=200)#don't need to return anything.
        except Exception as e:
            return HttpResponse(str(e),status=500)
    elif request.method == "PUT":#update company billing info
        #get billing details for user
        bi = getBillingDetails(request)
        if(len(bi) < 1):
            return HttpResponse("No set of billing details for this company.",status=500)
        else:
            bi = bi[0]
            try:
                customer = stripe.Customer.retrieve(bi.stripeCustomer)
            except Exception as e:
                return HttpResponse("No such stripe customer",status=404)
            data = JSONParser().parse(request)#parse incoming data
            customer.email = data.get('email') || customer.email
            customer.metadata = {
                "contact_phone" = data.get('phone'),
                "user_edit" = request.user.user.id,
                "company" = request.user.user.company.id,
            }
            customer.source = data.get('stripeToken') || customer.source
            try:
                customer.save()
                return HttpResponse(status=200)#don't need to return anything.
            except Exception as e:
                return HttpResponse(str(e),status=500)
    # elif request.method == "DELETE":
    #     bi = getBillingDetails(request)
    #     if(len(bi) < 1):
    #         return HttpResponse("no such billing detail.",status=404)
    #     else:
    #         bi = bi[0]
    #         try:
    #             customer = stripe.Customer.retrieve(bi.stripeCustomer)
    #             customer.delete()
    #             return HttpResponse("customer deleted.",status=200)
    #         except Exception as e:
    #             return HttpResponse("no such stripe customer", status=404)
    elif request.method == "GET":
        bi = getBillingDetails(request)
        if(len(bi) < 1):
            return HttpResponse("no such billing detail.",status=404)
        else:
            bi = bi[0]
            try:
                customer = stripe.Customer.retrieve(bi.stripeCustomer)
            except Exception as e:
                return HttpResponse("No such stripe customer",status=404)
            serializer = serializers.BillingInfo(bi)
            response = {
                "stripeCustomer": customer,
                "BillingInfo": serializer.data,
            }
            return JSONResponse(response, status=200)
    return HttpResponse(status=404)
def bills(request):
    if request.method = 'GET':
        pass#return list of all bills... and payment status
def payBill(request):#for unpaid bills where payment failed
	pass
#price updates handled manually as well as referral bonuses
def creditBalance(request):#current balance of available credits
	pass
#credit processing will be done automatically, bill issuing will be done automatically
