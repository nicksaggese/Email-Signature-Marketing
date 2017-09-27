from . import models
def buildEvent(request):
    data = request.META
    return {
        "referrer": data.get("HTTP_REFERER"),
        "remoteHost": data.get("REMOTE_HOST"),
        "remoteIP": data.get("REMOTE_ADDR"),
        "userAgent": data.get("HTTP_USER_AGENT"),
        "language": data.get("HTTP_ACCEPT_LANGUAGE"),
    }
#Billboard
def addBillboardInfo(e,employee,photo,billboard):
    e["media"]=photo
    e["employee"]=employee
    e["billboardMedia"]=billboard
    return e
def displayBillboard(request,employee,photo,billboard):
    e = buildEvent(request)
    e = addBillboardInfo(e,employee,photo,billboard)
    e["interaction"]="display"
    # e["target"]="billboard"
    e = models.Billboard(**e)
    e.save()
def clickBillboard(request,employee,photo,billboard):
    e = buildEvent(request)
    e = addBillboardInfo(e,employee,photo,billboard)
    e["interaction"]="click"
    # e["target"]="billboard"
    e = models.Billboard(**e)
    e.save()

def displayBillboardReferral(request,employee,photo,billboard):
    e = buildEvent(request)
    e["interaction"]="display"
    e = models.BillboardReferral(**e)
    e.save()
def clickBillboardReferral(request,employee,photo,billboard):
    e = buildEvent(request)
    e["interaction"]="click"
    e = models.BillboardReferral(**e)
    e.save()
#internal referral program
from directory import models as directory_models
def refParams(request):
    return {
        "party": request.query_params.get('ref_party'),#specific employee, user, proprietary
		"source": request.query_params.get('ref_source')#page the request was made on
    }
def buildOnsiteEvent(request):
    e= buildEvent(request)
    e["page"] = request.query_params.get('ref_page')
    return e
def refChainEvent(request,ref_chain):
    e = buildOnsiteEvent(request)
    e["chain"] = ref_chain
    return e
def employeeReferral(ref_chain,request):
    try:
        employee = directory_models.Employee.objects.get(url=request.query_params.get('ref_party'))
    except directory_models.Employee.DoesNotExist:
        pageView(ref_chain,request)#fallback
    e = refChainEvent(request,ref_chain)
    e["employee"] = employee.id
    e["source"] = request.query_params.get('ref_source')
    er = models.EmployeeReferral(**e)
    er.save()
def userReferral(ref_chain,request):
    try:
        user = directory_models.User.objects.get(url=request.query_params.get('ref_party'))
    except directory_models.User.DoesNotExist:
        pageView(ref_chain,request)#fallback
    e = refChainEvent(request,ref_chain)
    e["user"] = user.id
    e["source"] = request.query_params.get('ref_source')
    ur = models.UserReferral(**e)
    ur.save()

def proprietaryReferral(ref_chain,request):
    pageView(request,ref_chain)#TODO not setup yet so default to pageview

def pageView(ref_chain,request):
    e = refChainEvent(request,ref_chain)
    pv = models.PageView(**e)
    pv.save()
def getRefChain(request):
    ref_chain = request.session.get('ref_chain')
    if(ref_chain is None):#if session cookie found lookup ref chain, apply new event
        r = models.ReferralChain()
        r.save()
        request.session['ref_chain'] = r.id
        ref_chain = r.id
    return ref_chain

def companyOnboard(request,company):
    ref_chain = getRefChain(request)
    co = models.CompanyOnboard(chain=ref_chain,company=company)
    co.save()

def employeeOnboard(request,employee):
    ref_chain = getRefChain(request)
    e = models.EmployeeOnboard(chain=ref_chain,employee=employee)
    e.save()
