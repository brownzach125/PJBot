from bwapi_mirror_wrapper.bwapi.UnitType import UnitType
from bwapi_mirror_wrapper.bwapi.TilePosition import TilePosition

from bwapi_mirror_wrapper.bwapi.Unit import Unit
from bwapi_mirror_wrapper.bwapi import UnitType


class BuildJob(object):
    def __init__(self, worker, unit_type, position):
        self.worker = worker
        self.unit_type = unit_type
        self.position = position


class BuilderExpert:
    def unit_destroyed(self, unit: Unit) -> None:
        pass
    def unit_morphed(self, unit: Unit) -> None:
        pass
    def create_build_job(self, worker: Unit, unit_type: UnitType, position: TilePosition):
        pass
    def on_frame(self) -> None:
        pass
    def get_build_tile(self, builder: Unit, building_type: UnitType, start_tile: TilePosition, max_distance=40) -> None:
        pass
