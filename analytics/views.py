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
from . import models
from directory.permissions import StandardUserPermissions

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

@api_view(['GET'])
@permission_classes((StandardUserPermissions,))
def billboard(request):
    if request.method == 'GET':
        try:
            b = campaign_billboard.objects.get(id=request.query_params.get("id"))
        except campaign_billboard.DoesNotExist:
            return HttpResponse(status=404)
        displays = len(models.Billboard.objects.filter(interaction="display",target="billboard",billboard=b))
        clicks = len(models.Billboard.objects.filter(interaction="click",target="billboard",billboard=b))
        ctr = 0
        if displays is not 0:
            ctr = clicks / float(displays)
        data = {
            "displays":displays,
            "clicks":clicks,
            "ctr":ctr,
            "billboard":b.id,
        }
        return JSONResponse(data,status=200)
    else:
        return HttpResponse("No such billboard found",status=400)
