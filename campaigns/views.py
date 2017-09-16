# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view,permission_classes
from . import models
from . import serializers

from rest_framework import permissions
from rest_framework.permissions import AllowAny
from directory.permissions import StandardUserPermissions
from directory.models import Employee
import os
import imgur
import currentBillboard

from datetime import datetime
import pytz
from dateutil import parser as datetime_parser
from analytics import actions as analytics_actions
from directory.helpers import disallowChanges, userDateParse

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)
# disallowed = ["company",]
# data = disallowChanges(disallowed,data)
@api_view(['POST','PUT',])
@permission_classes((StandardUserPermissions,))
def billboardPhoto(request):
	if request.method == 'POST':#create billboard with photo at same time
		data = JSONParser().parse(request)#parse incoming data
		photo = data.get('photo')
		data = data.get('billboard')
		data["company"] = request.user.user.company.id
		#make sure now broken dates
		try:
			start = data.get('start')
			if(start is not None):
				data['start'] = userDateParse(request,start)
				if(data.get('start') < datetime.now()):
					data['start'] = datetime.now()
			end = data.get('end')
			if end is not None:
				data['end'] = userDateParse(request,end)
				if(data.get('end') < datetime.now()):
					data['end'] = None
		except Exception as e:
			pass #do nothing if they aren't specified
		serializer = serializers.BillboardSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			billboard = serializer.data

			#photo section
			try:
				# photo = data.get('photo')
				r = imgur.createPhotoImgur(photo)
				photo = {
					'company':request.user.user.company.id,
					# 'billboard': data['billboard'],
					'imgurDeleteHash': r.get('data').get('deletehash'),
					'imgurId': r.get('data').get('id'),
					'imgurLink':r.get('data').get('link'),
				}
			except Exception as e:
				return HttpResponse("Photo error.",status=404)
			serializer = serializers.PhotoSerializer(data=photo)
			if serializer.is_valid():
				serializer.save()

				disallowed = ["imgurId","imgurDeleteHash"]
				photo = disallowChanges(disallowed,serializer.data)#for response

				data = {
					'company': request.user.user.company.id,
					'billboard': billboard.get('id'),
					'photo': serializer.data.get('id'),
				}
				serializer = serializers.BillboardMediaSerializer(data=data)
				if serializer.is_valid():
					serializer.save()
					billboardMedia = serializer.data
					response = {
						"billboardMedia":billboardMedia,
						"photo":photo,
						"billboard":billboard,
					}
					return JSONResponse(response,status=200)
	elif request.method == 'PUT':#add photo to billboard
		data = JSONParser().parse(request)#parse incoming data
		try:
			billboard = models.Billboard.objects.get(id=data.get('billboard'))
		except models.Billboard.DoesNotExist:
			return HttpResponse("No billboard at " + str(data.get('billboard')),status=404)
		try:
			r = imgur.createPhotoImgur(data.get('photo'))
			photo = {
				'company':request.user.user.company.id,
				# 'billboard': data['billboard'],
				'imgurDeleteHash': r.get('data').get('deletehash'),
				'imgurId': r.get('data').get('id'),
				'imgurLink':r.get('data').get('link'),
			}
		except Exception as e:
			return HttpResponse("Photo error.",status=404)
		serializer = serializers.PhotoSerializer(data=photo)
		if serializer.is_valid():
			serializer.save()
			data = {
				'company': request.user.user.company.id,
				'billboard': billboard.id,
				'photo': serializer.data.get('id'),
			}
			serializer = serializers.BillboardMediaSerializer(data=data)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data, status=200)
	return JSONResponse(serializer.errors, status=400)


@api_view(['PUT','DELETE'])
@permission_classes((StandardUserPermissions,))
def billboardMedia(request):
	# if request.method == 'POST':
	# 	data = JSONParser().parse(request)#parse incoming data
	# 	data["company"] = request.user.user.company.id
	# 	serializer = serializers.BillboardMedia(data=photo)
	# 	if serializer.is_valid():
	# 		serializer.save()
	# 		return JSONResponse(serializer.data,status=200)
	# elif request.method == 'GET':
	# 		try:
	# 			b = models.Photo.objects.get(id=request.query_params.get('id'))
	# 			serializer = serializers.BillboardMediaSerializer(b)
	# 			#remove sec sensitive
	# 			d= serializer.data
	# 			return JSONResponse(d, status=200)
	# 		except models.BillboardMedia.DoesNotExist:
	# 			return HttpResponse("No billboard media at this id.", status=404)
	if request.method == 'PUT':
		data = JSONParser().parse(request)#parse incoming data
		disallowed = ["company","billboard","photo"]
		data = disallowChanges(disallowed,data)
		try:
			b = models.BillboardMedia.objects.get(id=data.get("id"))
		except models.BillboardMedia.DoesNotExist:
			return HttpResponse(data,status=404)
		serializer = serializers.BillboardMediaSerializer(b,data=data,partial=True)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=200)
	elif request.method == 'DELETE':
		data = JSONParser().parse(request)
		try:
			b = models.BillboardMedia.objects.get(id=data.get('id'))
			#delete photo on imgur
			serializer = serializers.BillboardMediaSerializer(b)
			b.delete()#delete billboard
			return JSONResponse(serializer.data,status=200)
		except models.BillboardMedia.DoesNotExist:
			return HttpResponse("No billboard media for this id",status=404)
	return JSONResponse(serializer.errors, status=400)
@api_view(['POST','GET','DELETE'])
@permission_classes((StandardUserPermissions,))
def photo(request):
		if request.method == 'POST':#create photo on imgur and upload at same time
			data = JSONParser().parse(request)#parse incoming data
			#save photo
			r = imgur.createPhotoImgur(data.get('photo'))
			photo = {
				'company':request.user.user.company.id,
				# 'billboard': data['billboard'],
				'imgurDeleteHash': r.get('data').get('deletehash'),
				'imgurId': r.get('data').get('id'),
				'imgurLink':r.get('data').get('link'),
			}
			serializer = serializers.PhotoSerializer(data=photo)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data,status=200)
		elif request.method == 'GET':
				try:
					b = models.Photo.objects.get(id=request.query_params.get('id'))
					serializer = serializers.PhotoSerializer(b)
					#remove sec sensitive
					d= serializer.data
					d.pop('imgurDeleteHash', None)
					d.pop('imgurId', None)
					return JSONResponse(d, status=200)
				except models.Photo.DoesNotExist:
					return HttpResponse("No photo at this id.", status=404)
		elif request.method == 'DELETE':
			data = JSONParser().parse(request)
			try:
				b = models.Photo.objects.get(id=data.get('id'))
				#delete photo on imgur
				serializer = serializers.PhotoSerializer(b)
				imgur.deletePhotoImgur(b.imgurDeleteHash)
				b.delete()#delete billboard
				return JSONResponse(serializer.data,status=200)
			except models.Photo.DoesNotExist:
				return HttpResponse("No photo for this id",status=404)
		return JSONResponse(serializer.errors, status=400)

@api_view(['POST','GET','PUT','DELETE'])
@permission_classes((StandardUserPermissions,))
def billboard(request):
	query_type = request.query_params.get('type')
	if query_type == "single":
		if request.method == 'POST':
			data = JSONParser().parse(request)#parse incoming data
			data["company"] = request.user.user.company.id
			#make sure now broken dates
			try:
				start = data.get('start')
				if(start is not None):
					data['start'] = userDateParse(request,start)
					if(data.get('start') < datetime.now()):
						data['start'] = datetime.now()
				end = data.get('end')
				if end is not None:
					data['end'] = userDateParse(request,end)
					if(data.get('end') < datetime.now()):
						data['end'] = None
			except Exception as e:
				pass #do nothing if they aren't specified
			serializer = serializers.BillboardSerializer(data=data)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data,status=200)
		elif request.method == 'GET':
				response = {}
				try:
					b = models.Billboard.objects.get(id=request.query_params.get('id'))
					serializer = serializers.BillboardSerializer(b)
					response["billboard"] = serializer.data
					medias = models.BillboardMedia.objects.filter(billboard=b.id)
					serializer = serializers.BillboardMediaSerializer(medias,many=True)
					response["billboardMedia"] = serializer.data
					photos = []
					for photo in medias:
						try:
							photos.append(models.Photo.objects.get(id=photo.id))
						except models.Photo.DoesNotExist:
							continue
					serializer = serializers.PhotoSerializer(photos,many=True)
					response["photos"] = serializer.data
					return JSONResponse(response, status=200)
				except models.Billboard.DoesNotExist:
					return HttpResponse("No billboard with this id",status=404)
		elif request.method == 'PUT':
			data = JSONParser().parse(request)#parse incoming data
			disallowed = ["company",]
			data = disallowChanges(disallowed,data)
			try:
				b = models.Billboard.objects.get(id=data.get("id"))
			except models.Billboard.DoesNotExist:
				return HttpResponse(data,status=404)
			#TODO convert to timezone aware
			try:
				start = data.get('start')
				if(start is not None):
					data['start'] = userDateParse(request,start)
					if(data.get('start') < datetime.now()):
						data['start'] = b.start#can only start once
				end = data.get('end')
				if end is not None:
					data['end'] = userDateParse(request,end)
					if (data.get('end') < datetime.now()):
						data['end'] = datetime.now()
			except Exception as e:
				pass #do nothing if they aren't specified

			serializer = serializers.BillboardSerializer(b,data=data,partial=True)

			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data, status=200)

		elif request.method == 'DELETE':
			data = JSONParser().parse(request)#parse incoming data
			try:
				b = models.Billboard.objects.get(id=data.get('id'))
				serializer = serializers.BillboardSerializer(b)
				b.delete()
				return JSONResponse(serializer.data,status=200)
			except models.Billboard.DoesNotExist:
				return HttpResponse(data,status=404)
		else:
			return HttpResponse(status=404)
		return JSONResponse(serializer.errors, status=400)
	elif query_type == "list":
		if request.method == 'GET':
				try:
					b = models.Billboard.objects.filter(company = request.user.user.company)
					serializer = serializers.BillboardSerializer(b, many=True)
					return JSONResponse(serializer.data, status=200)
				except models.Billboard.DoesNotExist:
					return HttpResponse(status=404)
		elif request.method == 'DELETE':
			data = JSONParser().parse(request)#parse incoming data
			response = []
			for billboard in data:
				try:
					b = models.Billboard.objects.get(id=billboard)
					serializer = serializers.BillboardSerializer(b)
					b.delete()
					response.append(serializer.data)
				except models.Billboard.DoesNotExist:
					continue#effectively do nothing
			if len(response) is 0:
				return HttpResponse(data,status=404)
			else:
				return JSONResponse(response, status=200)
		else:
			return HttpResponse(status=404)
		return JSONResponse(serializer.errors, status=400)
	else:
		return HttpResponse(status=404)

	#find most recent campaign of groups
@api_view(['GET'])
@permission_classes((AllowAny, ))
def display(request):
	if request.method == 'GET':
		try:
			employee = request.query_params.get('e')
			print employee
			if(employee != None):
				employee = Employee.objects.get(url=employee)
			else:
				raise Employee.DoesNotExist
		except Employee.DoesNotExist:
			return HttpResponse("No employee matches query.",status=404)

		cc = currentBillboard.findCurrentCampaign(employee)
		if(cc is None):
			return HttpResponse("Billboard improperly configured. No billboard.",status=404)

		medias = models.BillboardMedia.objects.filter(billboard=cc)
		photo = None
		if(len(medias) > 0):
			photo = medias[0].photo
		else:
			return HttpResponse("Billboard improperly configured. No photo.",status=404)
		analytics_actions.displayBillboard(request,employee,photo,cc)
		return redirect(photo.imgurLink)#redirects to real photo
	return HttpResponse(status=404)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def clickthrough(request):
	if request.method == 'GET':
		employee = request.query_params.get('e')
		target = request.query_params.get('t')
		if(employee != None):
			try:
				employee = Employee.objects.get(url=employee)
			except Employee.DoesNotExist:
				return HttpResponse("No employee matches query.",status=404)
		else:
			print employee
			return HttpResponse("No employee specified.",status=404)

		cc = currentBillboard.findCurrentCampaign(employee)
		if(cc is None):
			return redirect("https://"+employee.company.domain+"/")

		medias = models.BillboardMedia.objects.filter(billboard=cc)
		photo = None
		if(len(medias) > 0):
			photo = medias[0].photo
		else:
			return HttpResponse("Billboard improperly configured. No photo.",status=404)

		if(target == "r"):#target is referral
			space = '%20'
			#increment viral ctr
			print "got here"
			analytics_actions.clickViral(request,employee,photo,cc)
			return redirect('https://robinboard.com/viral?ename='+employee.first+space+employee.last+'&cname='+employee.company.name+'&cdomain'+employee.company.domain)
		elif(target == "c"):#target is campaign
			#increment billboard ctr
			analytics_actions.clickBillboard(request,employee,photo,cc)
			return redirect(cc.targeturl)#redirects to real photo
	return HttpResponse(status=404)
	#get user based on param
	#increment ctr count
	#redirect to associated current Campaign
