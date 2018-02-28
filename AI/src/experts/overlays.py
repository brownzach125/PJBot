from bwapi_mirror_wrapper.bwapi.Color import Color
from bwapi_mirror_wrapper.bwapi.UnitType import UnitType
from bwapi_mirror_wrapper.bwta.BWTA import BWTA
from AI.src.blackboard import BlackBoard
from AI.src.subscribe import every
from AI.src import event_constants


bb = BlackBoard()

@every(event_constants.onFrame)
def frame():
    regions()
    base_locations()


def overlay_region(region, color):
    game = bb.game
    points = region.getPolygon().getPoints()
    for i in range(-1, len(points) - 1):
        point_a = points[i]
        point_b = points[i + 1]
        game.drawLineMap(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY(), color)
        #game.drawLineScreen(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY(), color)


def base_locations():
    locations = bb.base_locations
    for base_location in locations.values():
        townhall_location = base_location.getPosition()
        width = UnitType.Zerg_Extractor.width()
        height = UnitType.Zerg_Extractor.height()
        bb.game.drawBoxMap(townhall_location.getX() - width / 2, townhall_location.getY() - height / 2,
                           townhall_location.getX() + width / 2, townhall_location.getY() + height / 2, Color.Blue)


def regions():
    regions = bb.regions
    for region in regions.values():
        overlay_region(region, Color.Yellow)

