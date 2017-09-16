from django.core.mail import send_mail
def forgotPassword(user,temp_pass):
    try:
        subject = "Robinboard Password Reset Request"
        message = "Your temporary password is: " + temp_pass
        fromEmail = "nick@robinboard.com"
        to = [user.email,]
        send_mail(subject,message,fromEmail,to,fail_silently=False)
        return True
    except smtplib.SMTPException:
        return False

def confirmUserDomain():
    pass
