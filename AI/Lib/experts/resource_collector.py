from bwapi import UnitType

from expert import Expert
from pubsub import pub
from AI.Lib.subscribe import every
from AI.Lib.blackboard import BlackBoard

@every('onStart')
def construct():
    print 'construct resource collector'
    BlackBoard().res_collector = ResourceCollectorExpert('Resource Collector')

class ResourceCollectorExpert(Expert):
    def __init__(self, name):
        super(ResourceCollectorExpert, self).__init__(name)

        self.unit_trackers.append(self.bb.mineral_workers)
        self.unit_trackers.append(self.bb.gas_workers)
        self.bb.grab_worker = self.release_worker
        self.bb.return_worker = self.claim_worker
        self.bb.worker_available = self.worker_available
        self.bb.available_worker = self.worker_available
        pub.subscribe(self.onFrame, 'onFrame')

    def mineral_worker_destroy_callback(self, unit):
        del self.bb.mineral_workers[unit.getID()]

    def gas_worker_destroy_callback(self, unit):
        del self.bb.gas_workers[unit.getID()]

    def extractor_destroy_callback(self, unit):
        del self.bb.extractors[unit.getID()]

    def release_worker(self):
        bb = self.bb
        unit = bb.mineral_workers.itervalues().next()
        del bb.mineral_workers[unit.getID()]
        unit.abandon()
        return unit

    def claim_extractor(self, extractor):
        extractor.claimed = True
        extractor.owner = self
        bb = self.bb
        bb.extractors[extractor.getID()] = extractor
        extractor.workers = {}

    def assign_worker(self, worker):
        bb = self.bb
        for extractor in bb.extractors.values():
            # TODO: is three the magic number?
            if len(extractor.workers) < 3:
                extractor.workers[worker.getID()] = worker
                worker.gather_job = extractor
                worker.destroy_callback = self.gas_worker_destroy_callback
                bb.gas_workers[worker.getID()] = worker
                return

        closest_mineral = filter(lambda x: x.getType().isMineralField(), bb.game.neutral().getUnits())
        closest_mineral = min(closest_mineral, key=lambda x: worker.getDistance(x))
        if closest_mineral:
            worker.gather_job = closest_mineral
            worker.destroy_callback = self.mineral_worker_destroy_callback
            bb.mineral_workers[worker.getID()] = worker

    def claim_worker(self, unit):
        unit.claimed = True
        unit.owner = self
        self.assign_worker(unit)
        unit.stop()

    def worker_available(self):
        return len(self.bb.mineral_workers)

    def onFrame(self):
        bb = self.bb
        game = bb.game
        #TODO I should claim the minerals as well

        free_extractors = bb.get_friendly_x(UnitType.Zerg_Extractor)
        new_extractors = free_extractors.values()
        free_extractors.clear()

        for extractor in new_extractors:
            self.claim_extractor(extractor)

        # nit: I should check for every kind of worker on my side, but lol
        free_workers_dict = bb.get_friendly_x(UnitType.Zerg_Drone)
        new_workers = free_workers_dict.values()
        free_workers_dict.clear()

        for unit in new_workers:
            self.claim_worker(unit)

        for unit in filter(lambda x: x.isIdle(), bb.mineral_workers.values()):
            unit.gather(unit.gather_job, False)
        for unit in filter(lambda x: x.isIdle(), bb.gas_workers.values()):
            unit.gather(unit.gather_job.base, False)
