from AI.Lib.wrapper import Wrapped
from AI.Lib.blackboard import BlackBoard


class Expert(object):
    def __init__(self, name):
        self.name = name
        self.unit_trackers = []
        self.bb = BlackBoard()

#    def onFrame(self):
#        pass
#        #print self.name + " on Frame"
#
#    def onUnitDiscover(self, unit):
#        pass
#
#    def onUnitMorph(self, unit):
#        pass
#
#    def onUnitEvade(self, unit):
#        pass
#
#    def onUnitComplete(self, unit):
#        pass
#
#    def onUnitCreate(self, unit):
#        pass
#
#    def onUnitDestroy(self, unit):
        #pass



