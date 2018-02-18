import traceback
from bwapi import Color, DefaultBWListener, Mirror
from bwta import BWTA
from expert import ResourceCollectorExpert, UnitExpert
from blackboard import BlackBoard


def overlay(game):
    locations = BWTA.getBaseLocations()
    for index, base_location in enumerate(locations):
        n_points = len(locations)
        points = base_location.getRegion().getPolygon().getPoints()
        for i in range(-1, len(points) - 1):
            point_a = points[i]
            point_b = points[i + 1]
            game.drawLineMap(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY(), Color.Yellow)
            game.drawLineScreen(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY(), Color.Yellow)


class Bot(DefaultBWListener):
    def __init__(self):
        self.mirror = Mirror()
        self.game = None
        self.player = None
        self.experts = []
        bb = BlackBoard()

    def run(self):
        self.mirror.getModule().setEventListener(self)
        self.mirror.startGame()

    def onEnd(self, isWinner):
        pass
    
    def onNukeDetect(self, target):
        pass
    
    def onUnitCreate(self, unit):
        pass
        #print "New Unit Discovered"
    
    def onUnitDiscover(self, unit):
        try:
            for expert in self.experts:
                expert.onUnitDiscover(unit)
        except Exception as e:
            print e
            traceback.print_exc()
        
    def onStart(self):
        # Due to a nastyness with pydevd finding the location of atexit and threading
        # I put things in try catches so I'll see them happen instead of the bot silently dying
        try:
            self.game = self.mirror.getGame()
            self.player = self.game.self()
            bb = BlackBoard()
            bb.player = self.player
            bb.game = self.game

            print "Analyzing map..."
            BWTA.readMap()
            BWTA.analyze()
            print "Map data ready"

            self.experts.append(UnitExpert("Unit Expert"))
            self.experts.append(ResourceCollectorExpert("Resource Collector"))

        except Exception as e:
            print e
            traceback.print_exc()
        
    def onFrame(self):
        try:
            overlay(self.game)
            for expert in self.experts:
                expert.onFrame()
        except Exception as e:
            print e
            traceback.print_exc()
            
        
        
    def onSendText(self, text):
        print text
        
    def onReceiveText(self, player, text):
        print text

