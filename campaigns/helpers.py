from . import models
from analytics import models as analytics_models
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
class ExpiredDisplay(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__(message)

        # Now for your custom code...
        self.errors = errors
        
def nextBillboard(medias):
    displays = analytics_models.Billboard.objects.filter(billboard=cc,interaction__icontains="display",target__icontains="billboard")
    if(len(displays) < cc.ABSample):#pre sample size, always serve lowest number served so far
        #continue ab
        topMedia = medias[0]
        topMediaDisplays = 0
        for media in medias:
            dcount = displays.filter(billboardMedia=media).count() #got min displayed photo
            if(dcount > topMediaDisplays):
                topMedia = media
                topMediaDisplays = dcount
                continue
            else:
                continue
        return topMedia #need media for current display
    else:#past sample size
        #find winner
        winners = medias.filter(ABWinner=True)
        if(len(winners) is 0):#no winner declared, declare one
            #ctr comparison
            clicks = analytics_models.Billboard.objects.filter(billboardMedia__billboard=cc.id,interaction__icontains="click",target__icontains="billboard")
            topMedia = medias[0]
            topMediaClicks = clicks.filter(billboardMedia=medias[0]).count()
            topMediaDisplays = displays.filter(billboardMedia=medias[0]).count() #got min displayed photo
            topCTR = 0.00
            if topMediaDisplays is not 0:
                topCTR = clicks / float(topMediaDisplays)
            for media in medias[1:]:
                ccount = clicks.filter(billboardMedia=media).count()
                dcount = displays.filter(billboardMedia=media).count() #got min displayed photo
                ctr = 0.00
                if(dcount is not 0):
                    ctr = ccount / float(dcount)
                if(ctr > topCTR):
                    topMedia = media
                    topMediaDisplays = dcount
                    topMediaClicks = ccount
                    topCTR = ctr
                    continue
                else:
                    continue
            #end for declare winners
            topMedia.ABWinner = True
            topMedia.save()#save to db
            return topMedia
        else:
            return winners[0]#top winner
