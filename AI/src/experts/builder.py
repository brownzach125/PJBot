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

    def log(self, message):
        full_message = "{0}@{1} {2}".format(self.worker.name, self.worker.getTilePosition(), message)
        logging.debug(full_message)

    def __init__(self, worker, unit_type, position, build_on_top_of_unit, builder_expert):
        self.bb = BlackBoard()
        self.worker = worker
        self.unit_type = unit_type
        self.position = position
        self.build_on_top_of_unit = build_on_top_of_unit
        self.builder_expert = builder_expert

        if self.build_on_top_of_unit:
            morph_unit = self.build_on_top_of_unit
        else:
            morph_unit = worker
        self.events = {
            self.on_frame: event_constants.onFrame,
            self.on_unit_destroy: event_constants.event_x_for_u(event_constants.onUnitDestroy, worker),
            self.on_unit_morph: event_constants.event_x_for_u(event_constants.onUnitMorph, morph_unit)
        }

        for handler, event in self.events.iteritems():
            pub.subscribe(handler, event)

        self.reserve_funds()
        bb.drones_on_way_to_build[worker.getID()] = worker

        self.log("Going to build a {0} at {1}".format(unit_type, position))


    def reserve_funds(self):
        bb.minerals_pending += self.unit_type.mineralPrice()
        bb.gas_pending += self.unit_type.gasPrice()

    def release_funds(self):
        bb.minerals_pending -= self.unit_type.mineralPrice()
        bb.gas_pending -= self.unit_type.gasPrice()

    def on_frame(self):
        if self.worker.dead and self.unit_type != UnitType.Zerg_Extractor:
            logging.error("This means he was killed in action!!!!! we need to do something about this")
            # in any case this guy is done
            self.job_over(None)
            return
        #explored = bb.game.isExplored(position.getX(), position.getY())
        self.worker.build(self.unit_type, self.position)

    def on_unit_destroy(self, unit):
        self.log("Died while building {0} at {1}".format(self.unit_type, self.position))
        if self.unit_type != UnitType.Zerg_Extractor:
            self.job_over()

    def on_unit_morph(self, unit):
        self.log("Morphed into {0}".format(self.unit_type))
        self.job_over(unit)

    def job_over(self, new_building):
        self.release_funds()
        self.worker.clean_ownership()
        del self.builder_expert.build_jobs[self.worker.getID()]
        del self.bb.drones_on_way_to_build[self.worker.getID()]

        for handler, event in self.events.iteritems():
            pub.unsubscribe(handler, event)

        if new_building:
            bb.add_unit_to_free(new_building)


class BuilderExpert:
    def __init__(self, name):
        self.bb = BlackBoard()
        self.name = name

        pub.subscribe(self.on_frame, event_constants.onFrame)
        pub.subscribe(self.unit_destroyed, event_constants.onUnitDestroy)
        pub.subscribe(self.unit_morphed, event_constants.onUnitMorph)

        self.build_jobs = {}

    def unit_destroyed(self, unit):
        pass

    def unit_morphed(self, unit):
        pass

    # Assumes this job is valid
    def create_build_job(self, worker, unit_type, position):
        bb = self.bb
        bb.minerals_pending += unit_type.mineralPrice()
        bb.gas_pending += unit_type.gasPrice()

        worker.build_job = BuildJob(worker, unit_type, position)
        self.bb.drones_on_way_to_build[worker.getID()] = worker

        #explored = bb.game.isExplored(position.getX(), position.getY())
        worker.build(unit_type, position)

    def on_frame(self):
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

            build_near = worker.getTilePosition()
            if next_unit_type == UnitType.Zerg_Hatchery:
                expansion_location = bb.next_expansion_location()
                bb.claim_build_location(expansion_location)
                position = expansion_location.getTilePosition()
                build_on_top_of_unit = None
            else:
                position, build_on_top_of_unit = self.get_build_tile(worker, next_unit_type, build_near)
            if not position:
                logging.error("Unable to find a location to build")
            self.build_jobs[worker.getID()] = BuildJob(worker, next_unit_type, position, build_on_top_of_unit, self)

            bb.build_schedule.pop(0)

    def get_build_tile(self, builder, building_type, start_tile, max_distance=40):
        bb = self.bb
        if building_type.isRefinery():
            extractors = bb.get_neutral_x(UnitType.Resource_Vespene_Geyser).values()
            extractors = filter(lambda x: x.exists(), extractors)
            if not len(extractors):
                logging.debug("There are no available extractors")
                return None, None
            # TODO I'm not a fan of this doing that here
            bb.remove_unit_from_free(extractors[0])
            return extractors[0].getTilePosition(), extractors[0]

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
                            return TilePosition(i, j), None

            distance += 2
        return None, None











