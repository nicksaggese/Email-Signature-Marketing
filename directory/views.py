# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from robinboardAPI.permissions import check_user_access, BadAccess
from django.contrib.auth import models as auth_models
from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view,permission_classes
from . import models
from . import serializers

from campaigns.models import Billboard

from rest_framework import permissions
from rest_framework.permissions import AllowAny
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from .helpers import disallowChanges, JSONResponse, domainFromEmail, checkEmail, processUserReturn, generateConfirmCode, userConfirmSequence

import os
from . import userEmails

# Create your views here.


@api_view(['POST'])
@permission_classes((AllowAny, ))
def initialize(request):#send in combo of nested user and email
	if request.method == 'POST':
		data = JSONParser().parse(request)#parse incoming data
		domain = domainFromEmail(data.get('user').get('email'))
		if(domain != data.get('company').get('domain')):
			return  HttpResponse(status=400)

		#domain and email domain are same
		#create company
		serializer = serializers.CompanySerializer(data=data.get('company'))
		if serializer.is_valid():
			serializer.save()

			c = models.Company.objects.get(domain=serializer.data.get('domain'))
			try:
				#create user
				data['user']['company'] = c.id
				data['user']['username'] = data.get('user').get('email')
				data['user']['password'] = make_password(data.get('user').get('password'))#necessary for serializers
				serializer = serializers.UserSerializer(data=data.get('user'))
				if serializer.is_valid():
					serializer.save()
					#send email for confirmation
					#gen confirm confirmCode
					email = data.get('user').get('email')
					first_name = data.get('user').get('first_name')
					last_name = data.get('user').get('last_name')
					userConfirmSequence(email,first_name,last_name, None)

					u = models.User.objects.get(email = email)
					full_user = auth_models.Permission.objects.get(codename="full_user")
					print full_user

					u.user_permissions.add(full_user)
					# disallowed = ["is_staff","is_active","is_superuser","confirmed","password","user_permissions","groups"]
					# data = disallowChanges(disallowed,serializer.data)
					#
					# data["permissions"] = "full_user"
					return JSONResponse(processUserReturn(u), status=200)#success in creating the resource
				else:
					c.delete()#remove company because user failed
			except Exception as e:
				c.delete()
				message = {
					"message":e.message
				}
				return JSONResponse(message,status=400)
	return JSONResponse(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def confirmUser(request):
	if request.method == "GET":
		confirmCode = request.query_params.get("confirmCode")
		email = request.query_params.get("email")
		try:
			user = models.User.objects.get(email=email)
		except models.User.DoesNotExist:
			return HttpResponse("invalid.",status=403)
		correct = generateConfirmCode(user.email,user.first_name,user.last_name)
		print correct
		print confirmCode
		if correct == confirmCode:
			user.confirmed = True
			user.save()
			return redirect("https://app.robinboard.com/confirmed",permanent=True)#redirect to app
		else:
			return HttpResponse("invalid code.",status=403)
@api_view(['POST',])
@permission_classes((AllowAny, ))
def forgotPassword(request):
	if request.method == 'POST':
		data = JSONParser().parse(request)#parse incoming data
		try:
			u = models.User.objects.get(email=data["email"])
		except models.User.DoesNotExist:
			return HttpResponse("User not found.",status=404)
		temp_pass =  User.objects.make_random_password()
		u.password = make_password(temp_pass)
		#send password email
		userEmails.forgotPassword(u,temp_pass)
		return HttpResponse(status=200)
	return HttpResponse(status=404)

@api_view(['POST','GET','PUT','DELETE'])
def company(request):
	if request.method == 'GET':
		try:
			u = request.user.user
			# b = models.Company.objects.get(id=request.query_params['id'])
			serializer = serializers.CompanySerializer(u.company)
			return JSONResponse(serializer.data, status=200)
		except models.Company.DoesNotExist:
			return HttpResponse(status=404)
	elif request.method == 'PUT':
		data = JSONParser().parse(request)#parse incoming data
		try:
			c = request.user.user.company
		except models.Company.DoesNotExist:
			return HttpResponse(status=404)
		disallowed = ["domain",]
		data = disallowChanges(disallowed,data)
		serializer = serializers.CompanySerializer(c,data=data,partial=True)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=200)
	elif request.method == 'DELETE':#TODO MAKE SURE ONLY 1 FULL USER LEFT BEFORE DELETE
		data = JSONParser().parse(request)#parse incoming data
		try:
			c = request.user.user.company
			if(c.domain == data.get('domain')):#have to enter domain to confirm delete
				serializer = serializers.CompanySerializer(c)
				c.delete()
				return JSONResponse(serializer.data, status=200)
			else:
				return HttpResponse(status=400)
		except models.Company.DoesNotExist:
			return HttpResponse(status=404)
	return JSONResponse(serializer.errors, status=400)

@api_view(['POST','GET','PUT','DELETE'])
def user(request):
	if request.method == 'POST':
		if(not request.user.has_perm('directory.full_user')):
			return HttpResponse("You cannot create new admins.",status=401)
		data = JSONParser().parse(request)#parse incoming data
		data["company"] = request.user.user.company.id#set company to current user
		data['username'] = data.get('email')
		temp_pass =  User.objects.make_random_password()
		data["password"] = make_password(temp_pass)
		if(not checkEmail(data,request)):
			return  HttpResponse(status=400)
		permission = data.get('permission',"half_user")

		serializer = serializers.UserSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			try:
				b=models.User.objects.get(email=data.get("email"))
				#provision permission
			except models.User.DoesNotExist:
				return HttpResponse("user didn't save properly.",status=404)
			try:
				if(permission == "full_user"):
					permission = auth_models.Permission.objects.get(codename="full_user")
				else:
					permission = auth_models.Permission.objects.get(codename="half_user")
				b.user_permissions.add(permission)
				userConfirmSequence(b.email,b.first_name,b.last_name,temp_pass)#setup confirm email for new user
				return JSONResponse(processUserReturn(b),status=200)
			except Exception as e:
				b.delete()
				return HttpResponse(e,status=500)


	if request.method == 'GET':#add sanitized list later, for now just get active user #TODO
		query_type = request.query_params.get("type")
		if(query_type == "current" or "single"):
			try:
				b = request.user.user
				if query_type == "single":
					if(not request.user.has_perm('directory.full_user')):
						return HttpResponse("You cannot access other users.",status=401)
					b = request.query_params.get('id')
					b = models.User.objects.get(id=b)
				return JSONResponse(processUserReturn(b), status=200)
			except models.User.DoesNotExist:
				return HttpResponse(status=404)
		elif(query_type == "list"):#list all users at company
			try:
				company = request.user.user.company
				users = models.User.objects.filter(company=company)
				response = []
				for user in users:
					response.append(processUserReturn(user))
				return JSONResponse(response, status=200)
			except models.User.DoesNotExist:
				return HttpResponse(status=404)
		else:
			return HttpResponse(status=404)
	elif request.method == 'PUT':#only current user #need ability to change this to edit other users.. or at least create, delete, promote, demote
		data = JSONParser().parse(request)#parse incoming data
		disallowed = ["is_staff","is_active","is_superuser","confirmed","user_permissions","groups"]
		data = disallowChanges(disallowed,data)
		full_user = auth_models.Permission.objects.get(codename="full_user")
		half_user = auth_models.Permission.objects.get(codename="half_user")
		#current
		print "here"
		if(data.get('type') == "current"):
			if(not checkEmail(data,request)):
				return  HttpResponse(status=400)
			try:
				b = request.user.user
			except models.User.DoesNotExist:
				return HttpResponse("no current user",status=404)
			serializer = serializers.UserSerializer(b,data=data,partial=True)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(processUserReturn(b), status=200)
		#promote
		elif(data.get('type') == "promote"):
			print "in here"
			if(not request.user.has_perm('directory.full_user')):
				return HttpResponse("You cannot access other users.",status=401)
			try:
				b = models.User.objects.get(id=data.get('id'),company=request.user.user.company)#no check needed
			except models.User.DoesNotExist:
				return HttpResponse("user does not exist.",status=404)
			print b.has_perm('directory.full_user')
			if(b.has_perm('directory.full_user')):
				return HttpResponse("User already fully promoted.", status=406)
			b.user_permissions.add(full_user)
			b.user_permissions.remove(half_user)
			return JSONResponse(processUserReturn(b), status=200)

		#demote
		elif(data.get('type') == "demote"):
			if(not request.user.user.has_perm('directory.full_user')):
				return HttpResponse("You cannot access other users.",status=401)
			try:
				b = models.User.objects.get(id=data.get('id'),company=request.user.user.company)#no check needed
			except models.User.DoesNotExist:
				return HttpResponse("user does not exist.",status=404)
			if(b.has_perm('directory.half_user')):
				return HttpResponse("User already fully demoted.", status=406)
			b.user_permissions.add(half_user)
			b.user_permissions.remove(full_user)
			return JSONResponse(processUserReturn(b), status=200)
		else:
			return HttpResponse(status=404)
		return HttpResponse(status=404)

	elif request.method == 'DELETE':#cannot delete current if no other full user... or deletes company
		data = JSONParser().parse(request)
		if(data.get('type') == "current"):
			try:
				u = request.user.user
			except models.User.DoesNotExist:
				return HttpResponse("Current user DNE.",status=404)
			full_user = auth_models.Permission.objects.get(codename="full_user")
			users = models.User.objects.filter(company=u.company,user_permissions=full_user).count()
			if((users < 1) and u.has_perm('directory.full_user')):
				return HttpResponse("No other admin users. Must promote another admin before deletion.",status=406)
			else:
				r = processUserReturn(u)
				u.delete()
				return JSONResponse(r,status=200)
		elif(data.get('type') == "other"):
			if(not request.user.has_perm('directory.full_user')):
				return HttpResponse("You cannot access other users.",status=401)
			try:
				b = models.User.objects.get(id=data.get('id'),company=request.user.user.company)
				if(b == request.user.user):
					return HttpResponse("Wrong route to delete current user, use type=current",status=406)
				b.delete()
			except models.User.DoesNotExist:
				return HttpResponse(status=404)
		else:
			return HttpResponse(status=404)

		try:
			b = models.User.objects.get(id=data.get('id'),company=request.user.user.company)
			b.delete()
		except models.User.DoesNotExist:
			return HttpResponse(status=404)
	return JSONResponse(serializer.errors, status=400)


import xxhash, random
def createEmployeeURL(employee):
    return xxhash.xxh64(employee.get('first')+employee.get('last')+employee.get('email')+str(random.randint(1,1000))).hexdigest()

#add edit delete individual Employee
@api_view(['POST','GET','PUT','DELETE'])
def employee(request):
	query_type = request.query_params.get('type')
	if(query_type == "single"):
		if request.method == 'POST':
			data = JSONParser().parse(request)#parse incoming data

			data["company"] = request.user.user.company.id#set company to current user

			if(not checkEmail(data,request)):
				return  HttpResponse(status=400)
			data['url'] = createEmployeeURL(data)
			serializer = serializers.EmployeeSerializer(data=data)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data, status=200)
		elif request.method == 'GET':
			try:
				b = models.Employee.objects.get(id=request.query_params.get('id'))
				check_user_access(request,b)

				serializer = serializers.EmployeeSerializer(b)
				return JSONResponse(serializer.data, status=200)
			except models.Employee.DoesNotExist:
				return HttpResponse(status=404)
			except BadAccess as b:
				return HttpResponse(b,status=401)
		elif request.method == 'PUT':
			data = JSONParser().parse(request)#parse incoming data
			disallowed = ["url","company"]
			data = disallowChanges(disallowed,data)
			if(not checkEmail(data,request)):
				return  HttpResponse(status=400)
			try:
				b = models.Employee.objects.get(id=data.get('id'))
				check_user_access(request,b)
			except models.Employee.DoesNotExist:
				return HttpResponse(status=404)
			except BadAccess as b:
				return HttpResponse(b,status=401)

			serializer = serializers.EmployeeSerializer(b,data=data,partial=True)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data, status=200)

		elif request.method == 'DELETE':#expand to all child objs TODO
			data = JSONParser().parse(request)#parse incoming data
			try:
				b = models.Employee.objects.get(id=data.get('id'))
				check_user_access(request,b)
				serializer = serializers.EmployeeSerializer(b)
				b.delete()
				return JSONResponse(serializer.data,status=200)
			except models.Employee.DoesNotExist:
				return HttpResponse(status=404)
			except BadAccess as b:
				return HttpResponse(b,status=401)

		return JSONResponse(serializer.errors, status=400)
	elif query_type == "list":#is list
		if request.method == 'POST':#parse csv locally
			data = JSONParser().parse(request)#parse incoming data
			for employee in data:
				if(not checkEmail(employee,request)):
					return  HttpResponse(status=400)
				employee["company"] = request.user.user.company.id#user/employee sanity
				employee['url'] = createEmployeeURL(employee)

				serializer = serializers.EmployeeSerializer(data=employee)
				if serializer.is_valid():
					serializer.save()
					return JSONResponse(serializer.data,status=200)
		if request.method == 'PUT':#parse csv locally
			employees = JSONParser().parse(request)#parse incoming data
			response = []
			for data in employees:
				disallowed = ["url","company"]
				data = disallowChanges(disallowed,data)
				if(not checkEmail(data,request)):
					return  HttpResponse(status=400)
				try:
					b = models.Employee.objects.get(id=data.get('id'))
					check_user_access(request,b)
				except models.Employee.DoesNotExist:
					continue
				except BadAccess as b:
					print "bad access"
					continue
				serializer = serializers.EmployeeSerializer(b,data=data,partial=True)
				if serializer.is_valid():
					serializer.save()
				response.append(serializer.data)
			if(len(response) is 0):
				return HttpResponse(status=404)
			return JSONResponse(serializer.data, status=200)

		elif request.method == 'GET':
				try:
					u = request.user.user
					b = models.Employee.objects.filter(company=u.company)
					serializer = serializers.EmployeeSerializer(b, many=True)#many true because list
					return JSONResponse(serializer.data, status=200)
				except models.Employee.DoesNotExist:
					return HttpResponse(status=404)

		elif request.method == 'DELETE':#add employee list, delete employee list, get all employees,
			data = JSONParser().parse(request)#parse incoming data
			response = []
			for idcode in data.get('employees'):
				try:
					b = models.Employee.objects.get(id=idcode)
					check_user_access(request,b)
					serializer = serializers.EmployeeSerializer(b)
					response.append(serializer.data)
					b.delete()
				except models.Employee.DoesNotExist:
					continue
				except BadAccess as b:
					print "bad access"
					continue
			if(len(response) is 0):
				return HttpResponse(status=404)
			else:
				return JSONResponse(response, status=200)
		return JSONResponse(serializer.errors, status=400)
	else:
		return HttpResponse(status=404)

# def groupEmployees(request):
# 	if request.method == 'PUT':#add employees to groups
# 	elif request.method == 'DELETE':#remove employees from group
# 	else:
# 		return HttpResponse(status=404)
# @api_view(['PUT',])
# @permission_classes((StandardUserPermissions,))
# def removeFromGroup(request):#removes a list of employees from a group
# 	if request.method == 'PUT':
# 		data = JSONParser().parse(request)#parse incoming data
# 		try:
# 			for group in data['groups']:
# 				g = models.Group.objects.get(id=group.id)
# 				for employee in group.employees:
# 					e = models.Employee.objects.get(id=employee.id)
# 					e.groups.remove(g)#remove from groups fields
# 			return HttpResponse(status=200)
# 		except models.Group.DoesNotExist:
# 			return HttpResponse(status=404)
# 		except models.Employee.DoesNotExist:
# 			return HttpResponse(status=404)
#
# @api_view(['PUT',])
# @permission_classes((StandardUserPermissions,))
# def addToGroups(request):
# 	pass
@api_view(['POST','GET','PUT','DELETE'])
def group(request):#get groups, delete groups.
	query_type = request.query_params.get('type')
	if(query_type == "list"):
		if request.method == 'GET':#get all groups at company
				try:
					u = request.user.user
					b = models.Group.objects.filter(company=u.company)
					serializer = serializers.GroupSerializer(b, many=True)#many true because list
					return JSONResponse(serializer.data, status=200)
				except models.Group.DoesNotExist:
					return HttpResponse(status=404)

		elif request.method == 'DELETE':#add employee list, delete employee list, get all employees,
				response = []
				data = JSONParser().parse(request)#parse incoming data
				for group in data:
					try:
						b = models.Group.objects.get(id=group)
						check_user_access(request,b)
						# employees = models.Employee.objects.filter(groups=b)
						# for e in employees:
						# 	e.groups.remove(b)#remove group from all employees
						# billboards = models.Billboard.objects.filter(groups=b)
						# for c in billboards:
						# 	c.groups.remove(b)#remove group from associated campaigns
						serializer = serializers.GroupSerializer(b)
						b.delete()
						response.append(serializer.data)
					except models.Group.DoesNotExist:
						continue
					except BadAccess as b:
						print "bad access"
						continue
				if(len(response) is 0):
					return JSONResponse(data, status=404)
				return JSONResponse(response, status=200)
	elif(query_type == "single"):
		if request.method == 'POST':
			data = JSONParser().parse(request)#parse incoming data
			data["group"]["company"] = request.user.user.company.id #auto-company
			serializer = serializers.GroupSerializer(data=data.get('group'))

			if serializer.is_valid():
				serializer.save()#create group
				#once serializer is saved... proceed to add employees
				group = models.Group.objects.get(company=serializer.validated_data.get('company').id,name=serializer.validated_data.get('name'))
				#create group with list of employees to boot
				for employee in data.get('employees'):#create group with list of employees to boot
					try:
						b = models.Employee.objects.get(id=employee)
						b.groups.add(group)
					except models.Employee.DoesNotExist:
						continue
				#return group
				return JSONResponse(serializer.data,status=200)
		elif request.method == 'GET':#get group details and employees inside it
				try:
					response = {}
					b = models.Group.objects.get(id=request.query_params.get('id'))
					check_user_access(request,b)
					serializer = serializers.GroupSerializer(b)
					response["group"] = serializer.data
					e = models.Employee.objects.filter(groups=b.id)
					serializer = serializers.EmployeeSerializer(e,many=True)
					response["employees"] = serializer.data
					return JSONResponse(response, status=200)
				except models.Group.DoesNotExist:
					return HttpResponse(status=404)
				except BadAccess as b:
					return HttpResponse(b,status=401)
		elif request.method == 'PUT':
			data = JSONParser().parse(request)#parse incoming data
			try:
				b = models.Group.objects.get(id=data.get('id'))
				check_user_access(request,b)
			except models.Group.DoesNotExist:
				return HttpResponse(status=404)
			except BadAccess as b:
				return HttpResponse(b,status=401)
			disallowed = ["company",]
			data = disallowChanges(disallowed,data)
			serializer = serializers.GroupSerializer(b,data=data,partial=True)
			if serializer.is_valid():
				serializer.save()
				return JSONResponse(serializer.data, status=200)
		elif request.method == 'DELETE':
			data = JSONParser().parse(request)#parse incoming data
			try:
				b = models.Group.objects.get(id=data.get('id'))
				check_user_access(request,b)
				#this removal should be automatic
				# employees = models.Employee.objects.filter(groups=b)
				# for e in employees:
				# 	e.groups.remove(b)#remove group from all employees
				# billboards = models.Billboard.objects.filter(groups=b)
				# for c in billboards:
				# 	c.groups.remove(b)#remove group from associated campaigns
				serializer = serializers.GroupSerializer(b)
				b.delete()
				return JSONResponse(serializer.data, status=200)
			except models.Group.DoesNotExist:
				return JSONResponse(data,status=404)
			except BadAccess as b:
				return HttpResponse(b,status=401)
		return JSONResponse(serializer.errors, status=400)
	else:
		return HttpResponse(status=404)
	return JSONResponse(serializer.errors, status=400)
