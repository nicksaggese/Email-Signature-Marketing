from django.core.mail import send_mail
def forgotPassword(user,temp_pass):
    try:
        subject = "Robinboard Password Reset Request"
        message = "Your temporary password is: " + temp_pass + " \nLogin with " + user.email + "at https://app.robinboard.com/login/"
        fromEmail = "support@robinboard.com"
        to = [user.email,]
        send_mail(subject,message,fromEmail,to,fail_silently=False)
        return True
    except smtplib.SMTPException:
        return False

def RequestUserConfirm(email,confirmCode,temp_pass):
    subject = "Robinboard Confirm Email and Company Domain"
    message = "<a href=\"http://localhost:8000/directory/confirm-user/?confirmCode=" + confirmCode + "&email=" + email + "\">Click to confirm your account and company domain with Robinboard.</a>"
    if(temp_pass is not None):
        message = message + "\nYour temporary password is: " + temp_pass
    fromEmail = "support@robinboard.com"
    to = [email,]
    send_mail(subject,message,fromEmail,to,fail_silently=False)
    return True
    #exceptions handled in outside catch

def RequestEmployeeConfirm(email,confirmCode):
    subject = "Robinboard Confirm Employee Email"
    message = "<a href=\"http://localhost:8000/directory/confirm-user/?confirmCode=" + confirmCode + "&email=" + email + "\">Click to confirm your employee account with with Robinboard.</a>"
    fromEmail = "support@robinboard.com"
    to = [email,]
    send_mail(subject,message,fromEmail,to,fail_silently=False)
    return True
    #exceptions handled in outside catch
