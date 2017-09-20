from directory import models
from datetime import datetime,timedelta
from django.utils import timezone
class BadAccess(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__(message)

        # Now for your custom code...
        self.errors = errors

def check_user_access(request,obj):
    #get user model
    u = request.user.user
    print u
    #validate object is part of same company
    if((u.confirmed is False) and (u.date_joined+timedelta(hours=1) < timezone.now())):
        message = "You have not yet confirmed your email address. Please check your inbox to confirm your account."
        raise BadAccess(message)
    if(obj.company == u.company):
        return True
    else:
        message = "You do not have access to this data."
        raise BadAccess(message)
