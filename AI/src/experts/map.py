from AI.src.wrapper import Wrapped
from AI.src.subscribe import every
from AI.src import event_constants as event_constants
from expert import Expert
from AI.src.blackboard import BlackBoard


bb = BlackBoard()

@every(event_constants.onStart)
def on_start():
    bb.max_expert = RegionGraph('Map Expert')


class Region(Wrapped):
    def __init__(self, base):
        super(Region, self).__init__(base)

        self.adjacent_regions = []

    def getAdjacentRegions(self):
        return self.adjacent_regions


class BaseLocation(Wrapped):
    def __init__(self, base):
        super(BaseLocation, self).__init__(base)

        self.claimed = False
        self.depth_from_player = -1


class RegionGraph(Expert):
    def __init__(self, name):
        super(RegionGraph, self).__init__(name)
        #self.name = name
        #self.bb = BlackBoard()
        self.bb.next_expansion_location = self.next_expansion_location
        self.bb.claim_build_location = self.claim_build_location
        self.bb.release_build_location = self.release_build_location

        self.choke_points = {}
        self.regions = {r.getCenter(): Region(r) for r in self.bb.BWTA.getRegions()}
        self.base_locations = {b.getTilePosition(): BaseLocation(b) for b in self.bb.BWTA.getBaseLocations()}
        self.start_location = self.base_lookup(self.bb.BWTA.getStartLocation(self.bb.player))
        self.start_location.claimed = True

        for region in self.regions.values():
            for choke in region.getChokepoints():
                if choke not in self.choke_points:
                    self.choke_points[choke] = []
                self.choke_points[choke].append(region)

        for region in self.regions.values():
            for choke in region.getChokepoints():
                region.adjacent_regions += filter(lambda x: x.getCenter() != region.getCenter(), self.choke_points[choke])

        expansions = []
        self.depth_traversal(expansions, lambda expansions, region, depth: expansions)

        def find_all_bases(base_locations, region, depth):
            for base_location in region.getBaseLocations():
                base_location = self.base_lookup(base_location)
                base_location.depth_from_player = depth
                base_locations.append(base_location)

        self.depth_traversal(expansions, find_all_bases)

        self.expansions = sorted(expansions, key=lambda location: location.depth_from_player)

    def region_lookup(self, raw_region):
        return self.regions[raw_region.getCenter()]

    def base_lookup(self, raw_base_location):
        return self.base_locations[raw_base_location.getTilePosition()]

    def depth_traversal(self, result, func):
        start_location = self.start_location
        func(result, self.region_lookup(start_location.getRegion()), 0)

        visited_regions = {}
        regions = self.region_lookup(start_location.getRegion()).getAdjacentRegions()
        depth = 1
        while regions:
            new_regions = []
            for region in regions:
                visited_regions[region.getCenter()] = region
                func(result, region, depth)
                new_regions += filter(lambda x: x.getCenter() not in visited_regions, region.getAdjacentRegions())
            regions = new_regions
            depth += 1

    def closest_baselocations(self, region):
        region = self.regions[region.getCenter()]
        base_locations = []
        visited_regions = {}
        regions = region.getAdjacentRegions()
        while regions and not base_locations:
            new_regions = []
            for region in regions:
                if region in visited_regions:
                    continue
                else:
                    visited_regions[region] = region

                base_locations += region.getBaseLocations()
                new_regions += region.getReachableRegions()
            regions = new_regions
        return base_locations

    def next_expansion_location(self):
        for expansion in self.expansions:
            if not expansion.claimed:
                return expansion

        return None

    def claim_build_location(self, location):
        location.claimed = True

    def release_build_location(self, location):
        location.claimed = True
