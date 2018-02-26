from bwapi_mirror_wrapper.bwapi import Color, UnitType
from bwapi_mirror_wrapper.bwta import BWTA
from AI.src.blackboard import BlackBoard
from AI.src.subscribe import every


bb = BlackBoard()
@every('onFrame')
def frame():
    regions()
    base_locations()


def overlay_region(region, color):
    game = bb.game
    points = region.getPolygon().getPoints()
    for i in range(-1, len(points) - 1):
        point_a = points[i]
        point_b = points[i + 1]
        game.drawLineMap(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY())
        game.drawLineScreen(point_a.getX(), point_a.getY(), point_b.getX(), point_b.getY())


def base_locations():
    locations = BWTA.getBaseLocations()
    for base_location in locations:
        region = base_location.getRegion()
        overlay_region(region, Color.Yellow)

        townhall_location = base_locations.getPosition()
        width = UnitType.Zerg_Hatchery
        bb.game.drawBoxScreen()


def regions():
    game = bb.game
    regions = BWTA.getRegions()
    for region in regions:
        overlay_region(region)