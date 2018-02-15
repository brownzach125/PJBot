from bwapi import UnitType
from blackboard_constants import CLAIMED, FREE_UNITS, MINERAL_MINING_WORKERS, \
                                 GAS_MINING_WORKERS, BWAPI_UNIT, LISTENER 


class Expert(object):
    def __init__(self, name, blackboard):
        self.name = name
        self.blackboard = blackboard

    def onFrame(self):
        pass
        #print self.name + " on Frame"
        
    def onUnitDiscover(self, unit):
        pass

# This expert's job is to be the on who iterates all units
# I don't want every expert to have to iterate through every unit I'd prefer if they only need to look
# at a few they care about
class UnitExpert(Expert):        
    def __init__(self, name, blackboard):
        super(UnitExpert, self).__init__(name, blackboard)

    def onUnitDiscover(self, bwapi_unit):
        print "We found a " + str(bwapi_unit.getType())
        
        unit = {
            BWAPI_UNIT: bwapi_unit,
            CLAIMED: False
        }

        if FREE_UNITS not in self.blackboard:
            self.blackboard[FREE_UNITS] = {}
        free_units = self.blackboard[FREE_UNITS]

        type = bwapi_unit.getType()
        
        if type not in free_units:
            free_units[type] = {}
       
        side = bwapi_unit.getPlayer().getID()
        if side not in free_units[type]:
            free_units[type][side] = {}
            
        free_units[type][side][bwapi_unit.getID()] = unit
        

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
        
        for worker in new_workers:
            worker[CLAIMED] = True
            bwapi_unit = worker[BWAPI_UNIT]
            self.blackboard[MINERAL_MINING_WORKERS][bwapi_unit.getID()] = worker
            
            closestMineral = filter(lambda x: x.getType().isMineralField(), game.neutral().getUnits())
            closestMineral = min(closestMineral, key=lambda x: bwapi_unit.getDistance(x))
            if closestMineral:
                bwapi_unit.gather(closestMineral, False)  
                
            
            

        
        
        
        
        
        
        
        
        
        
        
        