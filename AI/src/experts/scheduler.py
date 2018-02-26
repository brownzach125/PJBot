from bwapi_mirror_wrapper.bwapi.UnitType import UnitType

from AI.src.blackboard import BlackBoard
from expert import Expert
from pubsub import pub
from AI.src.subscribe import every


@every('onStart')
def construct():
    print 'construct scheduler'
    BlackBoard().scheduler = SchedulerExpert('Scheduler Expert')


class SchedulerExpert(Expert):
    def __init__(self, name):
        super(SchedulerExpert, self).__init__(name)
        pub.subscribe(self.onFrame, 'onFrame')

    def onFrame(self):
        bb = self.bb

        frame = bb.game.getFrameCount()
        if frame == 0:
            print "Schedule got to run"

            schedule = [
                UnitType.Zerg_Hatchery,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Spawning_Pool,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Overlord,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Extractor,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
                UnitType.Zerg_Drone,
            ]

            bb.build_schedule = schedule


