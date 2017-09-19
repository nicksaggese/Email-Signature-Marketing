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
    if(len(boards) > 0):
        minstart = boards[0]
        for billboard in boards:
            if billboard.start < minstart.start:
                minstart = billboard
        return minstart
    return None
