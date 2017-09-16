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
def addBillboardInfo(e,employee,photo,billboard):
    e["media"]=photo
    e["employee"]=employee
    e["billboard"]=billboard
    return e
def displayBillboard(request,employee,photo,billboard):
    e = buildEvent(request)
    e = addBillboardInfo(e,employee,photo,billboard)
    e["interaction"]="display"
    e["target"]="billboard"
    e = models.Billboard(**e)
    e.save()
def clickViral(request,employee,photo,billboard):
    e = buildEvent(request)
    e = addBillboardInfo(e,employee,photo,billboard)
    e["interaction"]="click"
    e["target"]="viral"
    e = models.Billboard(**e)
    e.save()
def clickBillboard(request,employee,photo,billboard):
    e = buildEvent(request)
    e = addBillboardInfo(e,employee,photo,billboard)
    e["interaction"]="click"
    e["target"]="billboard"
    e = models.Billboard(**e)
    e.save()
