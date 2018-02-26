import traceback
from bwapi_mirror_wrapper.bwapi.Mirror import Mirror
from bwapi_mirror_wrapper.bwapi.DefaultBWListener import DefaultBWListener
from bwapi_mirror_wrapper.bwta.BWTA import BWTA

from AI.src.blackboard import BlackBoard
from pubsub import pub
import logging
logging.basicConfig(
    handlers=[
        logging.StreamHandler()
    ],
    level=logging.DEBUG
)
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


class Bot(DefaultBWListener):
    def __init__(self):
        self.mirror = Mirror()
        self.game = None
        self.player = None
        self.experts = []
        self.bb = BlackBoard()

    def run(self):
        self.mirror.getModule().setEventListener(self)
        self.mirror.startGame()
    
    def _onEnd(self, isWinner):
        pass

    def _onNukeDetect(self, target):
        pub.sendMessage('onNukeDetect', target=target)
        
    def _onUnitDiscover(self, unit):
        pub.sendMessage('preUnitDiscover', unit=unit)
        #pub.sendMessage('onUnitDiscover', unit=unit)

    def _onUnitEvade(self, unit):
        pub.sendMessage('preUnitEvade', unit=unit)
        #pub.sendMessage('onUnitEvade', unit=unit)

    def _onUnitShow(self, unit):
        pub.sendMessage('preUnitShow', unit=unit)
        #pub.sendMessage('onUnitShow', unit=unit)
    
    def _onUnitHide(self, unit):
        pub.sendMessage('preUnitHide', unit=unit)
        #pub.sendMessage('onUnitHide', unit=unit)

    def _onUnitCreate(self, unit):
        pub.sendMessage('preUnitCreate', unit=unit)
        #pub.sendMessage('onUnitCreate', unit=unit)

    def _onUnitDestroy(self, unit):
        pub.sendMessage('preUnitDestroy', unit=unit)
        #pub.sendMessage('onUnitDestroy', unit=unit)

    def _onUnitMorph(self, unit):
        pub.sendMessage('preUnitMorph', unit=unit)
        #pub.sendMessage('onUnitMorph', unit=unit)

    def _onUnitRenegade(self, unit):
        pub.sendMessage('preUnitRenegade', unit=unit)
        pub.sendMessage('onUnitRenegade', unit=unit)

    def _onUnitComplete(self, unit):
        pub.sendMessage('preUnitComplete', unit=unit)
        #pub.sendMessage('onUnitComplete', unit=unit)
    
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
        
        pub.sendMessage('onStart')
        
    def _onSendText(self, text):
        bb = self.bb
        #exec(text)
        print text
        
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
        self.bb.game.sendText("/cheats")
        logerrors(self._onFrame)

    def onSendText(self, text):
        logerrors(partial(self._onSendText, text))

    def onReceiveText(self, player, text):
        logerrors(partial(self._onReceiveText, player, text))

    def onStart(self):
        logerrors(self._onStart)
