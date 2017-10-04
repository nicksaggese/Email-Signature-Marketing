# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from campaigns.models import Billboard as campaign_billboard
# Create your views here.
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny

from . import models

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

@api_view(['GET'])
def billboard(request):
    if request.method == 'GET':
        try:
            b = campaign_billboard.objects.get(id=request.query_params.get("id"),company=request.user.user.company)
        except campaign_billboard.DoesNotExist:
            return HttpResponse(status=404)

        displays = models.Billboard.objects.filter(interaction="display",target="billboard",billboardMedia__billboard=b.id).count()
        clicks = models.Billboard.objects.filter(interaction="click",target="billboard",billboardMedia__billboard=b.id).count()#updated to find billboard related to billboard media
        ctr = 0
        if displays is not 0:
            ctr = clicks / float(displays)
        data = {
            "displays":displays,
            "clicks":clicks,
            "ctr":ctr,
            "billboardMedia":b.id,
        }
        return JSONResponse(data,status=200)
    else:
        return HttpResponse("No such billboard found",status=400)

@api_view(['GET'])
@permission_classes((AllowAny,))
def trackingPixel(request):
	if request.method == "GET":
		ref_type = request.query_params.get('ref_type')#employee, user, proprietary
		# ref_target # translate the page into the appropriate target, be it employee signup or company onboard
		if(ref_type == "emp"):
			actions.employeeReferral(request)
		elif(ref_type == "user"):
			actions.userReferral(request)
		elif(ref_type == "prop"):#reengineer to use utm
			actions.proprietaryReferral(request)
		else:#pageview
			actions.pageView(ref_chain,request)
		return HttpResponse(status=200)#blank return
	return HttpResponse(status=404)
