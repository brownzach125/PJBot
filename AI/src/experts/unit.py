from bwapi_mirror_wrapper.bwapi.UnitType import UnitType

from AI.src.blackboard import BlackBoard
from AI.src import event_constants
from AI.src.wrapper import UnitWrapper

from pubsub import pub
from AI.src.subscribe import every
import logging


@every('onStart')
def construct():
    logging.info("Creating Unit Expert")
    BlackBoard().unit_expert = UnitExpert('Unit Expert')


# All units should be touched by the UnitExpert first. They will get wrapped here
class UnitExpert:
    def __init__(self, name):
        self.bb = BlackBoard()
        pub.subscribe(self.onUnitCreate, 'preUnitCreate')
        pub.subscribe(self.onUnitDiscover, 'preUnitDiscover')
        pub.subscribe(self.onUnitMorph, 'preUnitMorph')
        pub.subscribe(self.onUnitComplete, 'preUnitComplete')
        pub.subscribe(self.onUnitEvade, 'preUnitEvade')
        pub.subscribe(self.onUnitDestroy, 'preUnitDestroy')
        
    def find_or_wrap_unit(self, unit):
        bb = self.bb

        if unit.getID() not in bb.wrapped_unit_lookup:
            bb.wrapped_unit_lookup[unit.getID()] = UnitWrapper(unit)

        return bb.wrapped_unit_lookup[unit.getID()]

    def onUnitCreate(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)
        # TODO not sure if I want this
        #bb.add_unit_to_free(unit)
        print "Create: {0}: {1}".format(unit.getType(), unit.name)

        #pub.sendMessage(event_constants.event_x_for_u(event_constants.onUnitCreate, unit), unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitCreate, unit)

    def onUnitDiscover(self, unit):
        if unit.getType() == UnitType.Unknown:
            return

        bb = self.bb
        unit = self.find_or_wrap_unit(unit)
        print "Discover: {0}: {1}".format(unit.getType(), unit.name)
        # TODO could a unit be discovered that someone already owns??? I guess if the become inaccesible
        bb.add_unit_to_free(unit)
        #pub.sendMessage(event_constants.onUnitDiscover, unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitDiscover, unit)

    def onUnitMorph(self, unit):
        if unit.getType() == UnitType.Unknown:
            return

        bb = BlackBoard()
        unit = self.find_or_wrap_unit(unit)

        previous_type = unit.unit_type
        if not unit.claimed:
            bb.remove_unit_from_free(unit, previous_type)
        unit.unit_type = unit.getType()
        unit.unit_player = unit.getPlayer()

        #if unit.unit_type == UnitType.Zerg_Extractor and unit.getPlayer().getID() == bb.player_id:
        #    bb.extractor_morphed_callback(unit)
        #if unit.morph_callback:
        #    unit.morph_callback(unit)

        if not unit.claimed:
            bb.add_unit_to_free(unit)

        print "Morph: {0}: {1}".format(unit.getType(), unit.name)
        #pub.sendMessage(event_constants.onUnitMorph, unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitMorph, unit)

    def onUnitComplete(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)

        #if unit.complete_callback:
        #    unit.complete_callback(unit)

        if not unit.claimed:
            self.bb.add_unit_to_free(unit)

        print "Complete: {0}: {1}".format(unit.getType(), unit.name)
        #pub.sendMessage(event_constants.onUnitComplete, unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitComplete, unit)

    def onUnitEvade(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)
        print "Evade: {0}: {1}".format(unit.getType(), unit.name)
        #pub.sendMessage(event_constants.onUnitEvade, unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitEvade, unit)

    def onUnitDestroy(self, unit):
        bb = BlackBoard()
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)
        unit.dead = True

        del bb.wrapped_unit_lookup[unit.getID()]

        #if unit.destroy_callback:
        #    unit.destroy_callback(unit)

        print "Destroy: {0}: {1}".format(unit.getType(), unit.name)
        #pub.sendMessage(event_constants.onUnitDestroy, unit=unit)
        event_constants.send_event_x_for_u(event_constants.onUnitDestroy, unit)
