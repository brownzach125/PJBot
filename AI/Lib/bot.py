from bwapi import DefaultBWListener, Mirror

class Bot(DefaultBWListener):
    def __init__(self):
        self.mirror = Mirror()
        self.game = None
        self.self = None
        
    def run(self):
        self.mirror.getModule().setEventListener(self)
        self.mirror.startGame()
        
    def onUnitCreate(self, unit):
        print "New Unit Discovered"
        
    def onStart(self):
        self.game = self.mirror.getGame()
        print "On Start"
        
    def onFrame(self):
        print "On Frame"
