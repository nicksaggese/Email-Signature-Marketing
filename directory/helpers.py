def disallowChanges(disallowed,data):
	for d in disallowed:
		data.pop(d,None)
	return data
from datetime import datetime
import pytz
from dateutil import parser as datetime_parser
def userDateParse(request,dateString):
    return datetime_parser.parse(dateString, tzinfos={pytz.timezone(request.user.user.timezone)})
from django.http import HttpResponse
class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

import re
from . import models
def domainFromEmail(email):
	domain = re.search("@[\w.]+", email)
	domain = domain.group(0)[1:]#first in group, remove @
	return domain
def checkEmail(data,request):
	email = data.get('email')
	company = request.user.user.company.id
	if email is not None:
		domain = domainFromEmail(email)
		company = models.Company.objects.get(id=company)#get company for compare
		if(domain != company.domain):
			return False
	return True
from . import serializers
def processUserReturn(user):
	serializer = serializers.UserSerializer(user)
	disallowed = ["is_staff","is_superuser","password","user_permissions","groups"]
	d = disallowChanges(disallowed,serializer.data)
	#communicate permissions
	if(user.has_perm('directory.full_user')):
		d["permissions"] = 'full_user'
	else:
		d["permissions"] = 'half_user'
	return d
# Create your views here.


import hashlib,os
def generateConfirmCode(email,first,last):
	string = str(email)+str(first)+str(last)+str(os.environ.get('CONFIRM_EMAIL_SECRET'))
	return hashlib.md5(string).hexdigest()
from . import userEmails
def userConfirmSequence(email,first,last):
	confirmCode = generateConfirmCode(email,first,last)
	userEmails.RequestUserConfirm(email,confirmCode,tempPass)
