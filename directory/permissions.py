from rest_framework import permissions
from . import models
from datetime import datetime,timedelta
class StandardUserPermissions(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        #get user model
        u = request.user
        u = u.user
        #validate object is part of same company
        if((u.confirmed is False) and (u.date_joined +timedelta(hours=1)< datetime.now())):
            message = "You have not yet confirmed your email address. Please check your inbox to confirm your account."
            return False

        if(obj.company == u.company):
            return True
        else:
            message = "You do not have access to this data."
            return False
