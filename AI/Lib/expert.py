from bwapi import UnitType
from wrapper import Wrapped
from blackboard import BlackBoard


class Expert(object):
    def __init__(self, name):
        self.name = name

    def onFrame(self):
        pass
        #print self.name + " on Frame"
        
    def onUnitDiscover(self, unit):
        pass


# All units should be touched by the UnitExpert first. They will get wrapped here
class UnitExpert(Expert):
    def __init__(self, name):
        super(UnitExpert, self).__init__(name)

    def onUnitDiscover(self, unit):
        unit = Wrapped(unit)
        print "We found a " + str(unit.getType())

        bb = BlackBoard()
        free_units = bb.free_units

        type = unit.getType()
        
        if type not in free_units:
            free_units[type] = {}
       
        side = unit.getPlayer().getID()
        if side not in free_units[type]:
            free_units[type][side] = {}
            
        free_units[type][side][unit.getID()] = unit
        

class ResourceCollectorExpert(Expert):
    def __init__(self, name):
        super(ResourceCollectorExpert, self).__init__(name)
        
    def onFrame(self):
        bb = BlackBoard()
        player = bb.player
        game = bb.game
        
        # nit: I should check for every kind of worker on my side, but lol
        free_workers_dict = bb.free_units[UnitType.Zerg_Drone][player.getID()]
        new_workers = free_workers_dict.values()
        free_workers_dict.clear()
        
        for unit in new_workers:
            unit.claimed = True
            unit.owner = self
            bb.mineral_workers[unit.getID()] = unit
            
            closestMineral = filter(lambda x: x.getType().isMineralField(), game.neutral().getUnits())
            closestMineral = min(closestMineral, key=lambda x: unit.getDistance(x))
            if closestMineral:
                unit.gather(closestMineral, False)
                
            
            

        
        
        
        
        
        
        
        
        
        
        
        