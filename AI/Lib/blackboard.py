class BlackBoard:
    # Borg Design Pattern
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state

    game = None
    BWTA = None

    # Player
    player = None

    @property
    def player_id(self):
        return self.player.getID()

    @property
    def supply_available(self):
        return self.player.supplyTotal() - self.player.supplyUsed()

    @property
    def minerals_available(self):
        return self.player.minerals() - self.minerals_pending

    @property
    def gas_available(self):
        return self.player.gas() - self.gas_pending


    # Unit Expert
    wrapped_unit_lookup = {}
    free_units = {}

    # Resource Expert
    mineral_workers = {}
    gas_workers = {}
    grab_worker = None
    return_worker = None
    available_worker = None
    extractors = {}

    # Builder Expert
    hatcheries = {}
    waiting_on_minerals = False
    waiting_on_gas = False
    waiting_on_supply = False
    waiting_on_larva = False
    waiting_on_builder = False
    no_vespene_geyser_available = False
    @property
    def build_waiting_on_something(self):
        return self.waiting_on_minerals or self.waiting_on_gas or\
               self.waiting_on_supply or self.waiting_on_larva or self.waiting_on_builder
    drones_on_way_to_build = {}
    minerals_pending = 0
    gas_pending = 0


    # Scheduler Expert
    build_schedule = []


    # Utils
    def postion_to_key(self, position):
        return str(position)

    def get_friendly_x(self, unit_type):
        if not unit_type in self.free_units:
            return {}
        if not self.player_id in self.free_units[unit_type]:
            return {}
        return self.free_units[unit_type][self.player_id]

    def get_neutral_x(self, unit_type):
        if not unit_type in self.free_units:
            return {}
        if not self.game.neutral().getID() in self.free_units[unit_type]:
            return {}
        return self.free_units[unit_type][self.game.neutral().getID()]

    def add_unit_to_free(self, unit):
        type = unit.getType()

        if type not in self.free_units:
            self.free_units[type] = {}

        side = unit.getPlayer().getID()
        if side not in self.free_units[type]:
            self.free_units[type][side] = {}

        self.free_units[type][side][unit.getID()] = unit
        return

    def remove_unit_from_free(self, unit, previous_type=None):
        if not previous_type:
            previous_type = unit.getType()
        if previous_type in self.free_units and unit.getPlayer().getID() in self.free_units[previous_type]:
            del self.free_units[previous_type][unit.getPlayer().getID()][unit.getID()]
        pass
