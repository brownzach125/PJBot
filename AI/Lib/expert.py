from bwapi import UnitType
from blackboard_constants import CLAIMED, FREE_UNITS, MINERAL_MINING_WORKERS, \
                                 GAS_MINING_WORKERS, BWAPI_UNIT, LISTENER
from wrapper import Wrapped


class Expert(object):
    def __init__(self, name, blackboard):
        self.name = name
        self.blackboard = blackboard

    def onFrame(self):
        pass
        #print self.name + " on Frame"
        
    def onUnitDiscover(self, unit):
        pass


# All units should be touched by the UnitExpert first. They will get wrapped here
class UnitExpert(Expert):
    def __init__(self, name, blackboard):
        super(UnitExpert, self).__init__(name, blackboard)

    def onUnitDiscover(self, unit):
        unit = Wrapped(unit)
        print "We found a " + str(unit.getType())

        if FREE_UNITS not in self.blackboard:
            self.blackboard[FREE_UNITS] = {}
        free_units = self.blackboard[FREE_UNITS]

        type = unit.getType()
        
        if type not in free_units:
            free_units[type] = {}
       
        side = unit.getPlayer().getID()
        if side not in free_units[type]:
            free_units[type][side] = {}
            
        free_units[type][side][unit.getID()] = unit
        

class ResourceCollectorExpert(Expert):
    def __init__(self, name, blackboard):
        super(ResourceCollectorExpert, self).__init__(name, blackboard)
        
        self.blackboard[MINERAL_MINING_WORKERS] = {}
        self.blackboard[GAS_MINING_WORKERS] = {}
        
    def onFrame(self):
        player = self.blackboard[LISTENER].player
        game = self.blackboard[LISTENER].game
        
        # nit: I should check for every kind of worker on my side, but lol
        free_workers_dict = self.blackboard[FREE_UNITS][UnitType.Zerg_Drone][player.getID()]
        new_workers = free_workers_dict.values()
        free_workers_dict.clear()
        
        for unit in new_workers:
            unit.claimed = True
            unit.owner = self
            self.blackboard[MINERAL_MINING_WORKERS][unit.getID()] = unit
            
            closestMineral = filter(lambda x: x.getType().isMineralField(), game.neutral().getUnits())
            closestMineral = min(closestMineral, key=lambda x: unit.getDistance(x))
            if closestMineral:
                unit.gather(closestMineral, False)
                
            
            

        
        
        
        
        
        
        
        
        
        
        
        