from bwapi import UnitType

from AI.Lib.blackboard import BlackBoard

from expert import Expert
from AI.Lib.wrapper import UnitWrapper


# All units should be touched by the UnitExpert first. They will get wrapped here
class UnitExpert(Expert):
    def __init__(self, name):
        super(UnitExpert, self).__init__(name)

    def find_or_wrap_unit(self, unit):
        bb = BlackBoard()

        if unit.getID() not in bb.wrapped_unit_lookup:
            bb.wrapped_unit_lookup[unit.getID()] = UnitWrapper(unit)

        return bb.wrapped_unit_lookup[unit.getID()]

    def onUnitCreate(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        bb = self.bb
        unit = self.find_or_wrap_unit(unit)
        # TODO not sure if I want this
        #bb.add_unit_to_free(unit)
        print "Create: {0}: {1}".format(unit.getType(), unit.name)

    def onUnitDiscover(self, unit):
        if unit.getType() == UnitType.Unknown:
            return

        bb = self.bb
        unit = self.find_or_wrap_unit(unit)
        print "Discover: {0}: {1}".format(unit.getType(), unit.name)
        # TODO could a unit be discovered that someone already owns??? I guess if the become inaccesible
        bb.add_unit_to_free(unit)

    def onUnitMorph(self, unit):
        if unit.getType() == UnitType.Unknown:
            return

        bb = BlackBoard()
        unit = self.find_or_wrap_unit(unit)

        previous_type = unit.unit_type
        bb.remove_unit_from_free(unit, previous_type)
        unit.unit_type = unit.getType()
        unit.unit_player = unit.getPlayer()

        if unit.unit_type == UnitType.Zerg_Extractor and unit.getPlayer().getID() == bb.player_id:
            bb.extractor_morphed_callback(unit)
        if unit.morph_callback:
            unit.morph_callback(unit)

        if not unit.claimed:
            bb.add_unit_to_free(unit)

        print "Morph: {0}: {1}".format(unit.getType(), unit.name)

    def onUnitComplete(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)

        if unit.complete_callback:
            unit.complete_callback(unit)

        if not unit.claimed:
            self.bb.add_unit_to_free(unit)

        print "Complete: {0}: {1}".format(unit.getType(), unit.name)

    def onUnitEvade(self, unit):
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)
        print "Evade: {0}: {1}".format(unit.getType(), unit.name)

    def onUnitDestroy(self, unit):
        bb = BlackBoard()
        if unit.getType() == UnitType.Unknown:
            return
        unit = self.find_or_wrap_unit(unit)
        unit.dead = True

        del bb.wrapped_unit_lookup[unit.getID()]

        if unit.destroy_callback:
            unit.destroy_callback(unit)

        print "Destroy: {0}: {1}".format(unit.getType(), unit.name)
