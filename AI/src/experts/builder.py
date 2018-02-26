from bwapi_mirror_wrapper.bwapi.UnitType import UnitType
from bwapi_mirror_wrapper.bwapi.TilePosition import TilePosition
from bwapi import MouseButton

from pubsub import pub
import logging
from AI.src import event_constants
from AI.src.subscribe import every
from AI.src.blackboard import BlackBoard

bb = BlackBoard()
@every(event_constants.onStart)
def construct():
    BlackBoard().builder_expert = BuilderExpert('Builder Expert')


@every('mouse_click.' + str(MouseButton.M_LEFT))
def build_on_click(position):
    if bb.build_on_click:
        print position


class BuildJob(object):
    def __init__(self, worker, unit_type, position):
        self.worker = worker
        self.unit_type = unit_type
        self.position = position


class BuilderExpert:
    def __init__(self, name):
        self.bb = BlackBoard()
        self.name = name

        pub.subscribe(self.on_frame, event_constants.onFrame)
        pub.subscribe(self.unit_destroyed, event_constants.onUnitDestroy)
        pub.subscribe(self.unit_morphed, event_constants.onUnitMorph)

        self.workers_who_died_while_building_extractors = {}

    def unit_destroyed(self, unit):
        if unit.getID() not in self.bb.drones_on_way_to_build:
            return
        logging.debug("Unit destroyed while on way to build")

        build_type = unit.build_job.unit_type

        if build_type == UnitType.Zerg_Extractor:
            # TODO this was expected
            self.workers_who_died_while_building_extractors[unit.getID()] = unit
        else:
            # TODO this was not expected this is bad I should make the error message better and actaull do something
            logging.error("Unit Destroyed while on way to create")

    def unit_morphed(self, unit):
        bb = self.bb
        if unit.getID() not in self.bb.drones_on_way_to_build and unit.getType() != UnitType.Zerg_Extractor:
            return

        builder = unit
        if unit.getType() == UnitType.Zerg_Extractor:
            builder = None
            logging.debug("Extractor Morphed")
            for worker in self.workers_who_died_while_building_extractors.values():
                if worker.build_job.position == unit.getTilePosition():
                    del self.workers_who_died_while_building_extractors[worker.getID()]
                    builder = worker
                    break
            if not builder:
                logging.error("An extractor morphed without us having known that a worker had died to build it")

        job = builder.build_job
        bb.minerals_pending -= job.unit_type.mineralPrice()
        bb.gas_pending -= job.unit_type.gasPrice()

        # NOTE later I might choose to keep this unit
        job.worker.clean_ownership()
        del bb.drones_on_way_to_build[job.worker.getID()]
        bb.add_unit_to_free(unit)

    # Assumes this job is valid
    def create_build_job(self, worker, unit_type, position):
        bb = self.bb
        bb.minerals_pending += unit_type.mineralPrice()
        bb.gas_pending += unit_type.gasPrice()

        worker.build_job = BuildJob(worker, unit_type, position)
        self.bb.drones_on_way_to_build[worker.getID()] = worker
        worker.build(unit_type, position)

    def on_frame(self):
        bb = self.bb

        if len(self.workers_who_died_while_building_extractors):
            logging.error("This means he was killed in action!!!!! we need to do something about this")


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
        bb.waiting_on_builder = next_unit_type.isBuilding() and not bb.available_worker()

        if not bb.build_waiting_on_something:
            if not next_unit_type.isBuilding():
                larva = larva[0]
                larva.train(next_unit_type)
                bb.build_schedule.pop(0)
                return

            worker = bb.grab_worker()
            if not worker:
                self.bb.waiting_on_builder = True
                return

            worker.owner = self
            worker.claimed = True

            regions = bb.BWTA.getBaseLocations()
            start_location = bb.BWTA.getStartLocation(bb.player)
            start_tile_position = start_location.getTilePosition()

            build_near = worker.getTilePosition()
            if next_unit_type == UnitType.Zerg_Hatchery:
                position = self.get_build_tile(worker, next_unit_type, build_near)
                #start_location = bb.BWTA.getStartLocation(bb.player)
                #region = start_location.get
            else:
                position = self.get_build_tile(worker, next_unit_type, build_near)
            if not position:
                logging.error("Unable to find a location to build")
            self.create_build_job(worker, next_unit_type, position)

            bb.build_schedule.pop(0)

    def get_build_tile(self, builder, building_type, start_tile, max_distance=40):
        bb = self.bb
        if building_type.isRefinery():
            extractors = bb.get_neutral_x(UnitType.Resource_Vespene_Geyser).values()
            extractors = filter(lambda x: x.exists(), extractors)
            if not len(extractors):
                logging.debug("There are no available extractors")
                return None
            # TODO I'm not a fan of this doing that here
            bb.remove_unit_from_free(extractors[0])
            return extractors[0].getTilePosition()

        distance = 3
        while distance < max_distance:
            for i in range(start_tile.getX() - distance, start_tile.getY() + distance):
                for j in range(start_tile.getY() - distance, start_tile.getY() + distance):
                    if bb.game.canBuildHere(TilePosition(i, j), building_type, builder.base, False):
                        units_in_way = False
                        for unit in bb.game.getAllUnits():
                            if unit.getID() == builder.getID():
                                continue
                            if abs(unit.getTilePosition().getX()-i) < 4 and abs(unit.getTilePosition().getY() - j ) < 4:
                                units_in_way = True
                                break

                        creep_missing = False
                        if building_type.requiresCreep():
                            creep_missing = False
                            for k in range(i, i + building_type.tileWidth() + 1):
                                for I in range(j, j + building_type.tileHeight() + 1):
                                    if not bb.game.hasCreep(k, I):
                                        creep_missing = True
                                        break

                        if creep_missing:
                            continue

                        if not units_in_way:
                            return TilePosition(i, j)

            distance += 2












