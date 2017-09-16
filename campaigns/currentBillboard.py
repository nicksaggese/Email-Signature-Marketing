from . import models
from datetime import datetime
def findCurrentCampaign(employee):
    groups = employee.groups.all()
    #filter by group and date
    billboards = models.Billboard.objects.filter(groups=groups,start__lte=datetime.now())
    #end can be null
    boards = []
    for b in billboards:
        if(b.end is None):
            boards.append(b)
        elif(b.end > datetime.now()):
            boards.append(b)
    billboards = boards
    if(len(billboards) > 0):
        minstart = billboards[0]
        for billboard in billboards:
            if billboard.start < minstart.start:
                minstart = billboard
        return billboard
    return None
