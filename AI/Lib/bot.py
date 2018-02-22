import traceback
from bwapi import Color, DefaultBWListener, Mirror
from bwta import BWTA
from AI.Lib.experts import ResourceCollectorExpert, UnitExpert, BuilderExpert, SchedulerExpert
from AI.Lib.blackboard import BlackBoard
from pubsub import pub
import logging
import sys
from functools import partial

def logerrors(f):
    """ this function logs any exceptions that occur while f is being executed """
    try:
        f()
    except Exception:
        # grab the exception info and format without the outside layer
        # that way, we don't include this function in the call stack
        ei = sys.exc_info()
        logging.error(''.join(traceback.format_exception(ei[0], ei[1], ei[2].tb_next)))
    

def frame():
    bb = BlackBoard()
    overlay(bb.game)
pub.subscribe(frame, 'onFrame')

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

    def run(self):
        self.mirror.getModule().setEventListener(self)
        self.mirror.startGame()
    
    def _onEnd(self, isWinner):
        pass

    def _onNukeDetect(self, target):
        pub.sendMessage('onNukeDetect', target=target)
        
    def _onUnitDiscover(self, unit):
        pub.sendMessage('preUnitDiscover', unit=unit)
        pub.sendMessage('onUnitDiscover', unit=unit)

    def _onUnitEvade(self, unit):
        pub.sendMessage('preUnitEvade', unit=unit)
        pub.sendMessage('onUnitEvade', unit=unit)

    def _onUnitShow(self, unit):
        pub.sendMessage('preUnitShow', unit=unit)
        pub.sendMessage('onUnitShow', unit=unit)
    
    def _onUnitHide(self, unit):
        pub.sendMessage('preUnitHide', unit=unit)
        pub.sendMessage('onUnitHide', unit=unit)

    def _onUnitCreate(self, unit):
        pub.sendMessage('preUnitCreate', unit=unit)
        pub.sendMessage('onUnitCreate', unit=unit)

    def _onUnitDestroy(self, unit):
        pub.sendMessage('preUnitDestroy', unit=unit)
        pub.sendMessage('onUnitDestroy', unit=unit)

    def _onUnitMorph(self, unit):
        pub.sendMessage('preUnitMorph', unit=unit)
        pub.sendMessage('onUnitMorph', unit=unit)

    def _onUnitRenegade(self, unit):
        pub.sendMessage('preUnitRenegade', unit=unit)
        pub.sendMessage('onUnitRenegade', unit=unit)

    def _onUnitComplete(self, unit):
        pub.sendMessage('preUnitComplete', unit=unit)
        pub.sendMessage('onUnitComplete', unit=unit)
    
    def _onFrame(self):
        pub.sendMessage('onFrame')
    
    def _onStart(self):
        
        self.game = self.mirror.getGame()
        self.player = self.game.self()
        self.game.enableFlag(1)
        self.game.setLocalSpeed(42)
        bb = BlackBoard()
        bb.player = self.player
        bb.game = self.game
        bb.BWTA = BWTA

        print "Analyzing map..."
        BWTA.readMap()
        BWTA.analyze()
        print "Map data ready"
        
        self.experts.append(UnitExpert("Unit Expert"))
        self.experts.append(ResourceCollectorExpert("Resource Collector Expert"))
        self.experts.append(SchedulerExpert("Scheduler Expert"))
        self.experts.append(BuilderExpert("Build Expert"))
        pub.sendMessage('onStart')
        
    def _onSendText(self, text):
        print(eval(text))
        
    def _onReceiveText(self, player, text):
        print text

    def onEnd(self, isWinner):
        logerrors(partial(self._onEnd, isWinner))

    def onNukeDetect(self, target):
        logerrors(partial(self._onNukeDetect, target))

    def onUnitDiscover(self, unit):
        logerrors(partial(self._onUnitDiscover, unit))

    def onUnitEvade(self, unit):
        logerrors(partial(self._onUnitEvade, unit))

    def onUnitShow(self, unit):
        logerrors(partial(self._onUnitShow, unit))

    def onUnitHide(self, unit):
        logerrors(partial(self._onUnitHide, unit))

    def onUnitCreate(self, unit):
        logerrors(partial(self._onUnitCreate, unit))

    def onUnitDestroy(self, unit):
        logerrors(partial(self._onUnitDestroy, unit))

    def onUnitMorph(self, unit):
        logerrors(partial(self._onUnitMorph, unit))

    def onUnitRenegade(self, unit):
        logerrors(partial(self._onUnitRenegade, unit))

    def onUnitComplete(self, unit):
        logerrors(partial(self._onUnitComplete, unit))

    def onFrame(self):
        logerrors(self._onFrame)

    def onSendText(self, text):
        logerrors(partial(self._onSendText, text))

    def onReceiveText(self, player, text):
        logerrors(partial(self._onReceiveText, player, text))

    def onStart(self):
        logerrors(self._onStart)
