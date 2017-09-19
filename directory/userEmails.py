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

def RequestUserConfirm(email,confirmCode):
    print "in here"
    subject = "Robinboard Confirm Email and Company Domain"
    message = "<a href=\"http://localhost:8000/directory/confirm/?confirm=" + confirmCode + "\">Click to confirm your account and company domain with Robinboard.</a>"
    print message
    fromEmail = "nick@robinboard.com"
    to = [email,]
    send_mail(subject,message,fromEmail,to,fail_silently=False)
    return True
    #exceptions handled in outside catch
