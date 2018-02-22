from bwapi import UnitType

from AI.Lib.experts.expert import Expert
from pubsub import pub

class BuildJob(object):
    def __init__(self, worker, unit_type, position):
        self.worker = worker
        self.unit_type = unit_type
        self.position = position


class BuilderExpert(Expert):
    def __init__(self, name):
        super(BuilderExpert, self).__init__(name)
        self.unit_trackers.append(self.bb.drones_on_way_to_build)
        self.bb.extractor_morphed_callback = self.extractor_morphed
        pub.subscribe(self.onFrame, 'onFrame')

    def job_done(self, building):
        bb = self.bb
        job = building.build_job
        bb.minerals_pending -= job.unit_type.mineralPrice()
        bb.gas_pending -= job.unit_type.gasPrice()
        # NOTE later I might choose to keep this unit
        job.worker.abandon()
        del bb.drones_on_way_to_build[job.worker.getID()]

    def extractor_morphed(self, unit):
        print "Extractor Morphed Callback"
        bb = self.bb
        position = unit.getTilePosition()
        job = bb.jobs_to_build_extractors[bb.postion_to_key(position)]
        del bb.jobs_to_build_extractors[bb.postion_to_key(position)]
        self.job_done(job.worker)

    def building_morphed(self, unit):
        self.job_done(unit)

    # Assumes this job is valid
    def create_build_job(self, worker, unit_type, position):
        bb = self.bb
        bb.minerals_pending += unit_type.mineralPrice()
        bb.gas_pending += unit_type.gasPrice()

        worker.build_job = BuildJob(worker, unit_type, position)
        self.bb.drones_on_way_to_build[worker.getID()] = worker
        # NOTE I should add a destroy callback I should do that for all my experts
        if unit_type == UnitType.Zerg_Extractor:
            bb.jobs_to_build_extractors[bb.postion_to_key(position)] = worker.build_job
        else:
            worker.morph_callback = self.building_morphed

        worker.build(unit_type, position)


    def onFrame(self):
        bb = self.bb
        free_hatcheries = bb.get_friendly_x(UnitType.Zerg_Hatchery)
        new_hatcheries = free_hatcheries.values()
        free_hatcheries.clear()

        for unit in new_hatcheries:
            unit.claimed = True
            unit.owner = self

            bb.hatcheries[unit.getID()] = unit

        if not bb.build_schedule:
            return

        next_unit_type = bb.build_schedule[0]
        larva = bb.get_friendly_x(UnitType.Zerg_Larva).values()
        bb.waiting_on_minerals = bb.minerals_available < next_unit_type.mineralPrice()
        bb.waiting_on_gas = bb.gas_available < next_unit_type.gasPrice()
        bb.waiting_on_supply = bb.supply_available < next_unit_type.supplyRequired()
        bb.waiting_on_larva = not next_unit_type.isBuilding() and not larva
        bb.waiting_on_worker = next_unit_type.isBuilding() and not bb.available_worker()

        if not bb.build_waiting_on_something:
            if not next_unit_type.isBuilding():
                larva = larva[0]
                larva.train(next_unit_type)
            if next_unit_type == UnitType.Zerg_Extractor:


                extractors = bb.get_neutral_x(UnitType.Resource_Vespene_Geyser).values()
                extractors = filter(lambda x: x.exists(), extractors)
                if not len(extractors):
                    print "No available geyser"
                    return

                hatchery = bb.hatcheries.itervalues().next()
                if not hatchery:
                    print "There is no hatchery what's even the point now?"
                    return

               # TODO I should ask for the closest worker
                worker = bb.grab_worker()
                if not worker:
                    self.bb.no_vespene_geyser_available = True
                    return
                worker.owner = self

                extractor = min(extractors, key=lambda x: x.getDistance(hatchery.getPosition()))
                bb.remove_unit_from_free(extractor)

                position = extractor.getTilePosition()

                self.create_build_job(worker, UnitType.Zerg_Extractor, position)
            bb.build_schedule.pop(0)












