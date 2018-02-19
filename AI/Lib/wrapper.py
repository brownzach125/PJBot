from names import get_first_name


class Wrapped(object):
    """
    This class allows you to wrap a preconstructed object transparently
    self.__dict___ holds wrapper attributes, self.base holds the
    wrapped objects attributes.

    For example:
    u = Wrapped(unit)
    # add an attribute to the wrapper
    u.nickname = 'Bob'
    # still allows access to the base object
    u.getPosition()
    """

    def __init__(self, base):
        self.__dict__['base'] = base

    def __getattr__(self, name):
        # check the wrapper first (so we can hide base attributes)
        if name in self.__dict__:
            return self.__dict__[name]
        # otherwise route it to base
        return getattr(self.__dict__['base'], name)

    def __setattr__(self, name, value):
        # if it's already in the wrapper, then change it there
        if name in self.__dict__:
            self.__dict__[name] = value
        # otherwise check the base
        elif hasattr(self.__dict__['base'], name):
            setattr(self.__dict__['base'], name, value)
        else:
            # otherwise add it to the wrapper
            self.__dict__[name] = value

    def __hasattr__(self, name):
        # check the wrapper first
        if self.__dict__[name]:
            return True
        # and check the base
        return hasattr(self.__dict__['base'], name)


class UnitWrapper(Wrapped):
    def __init__(self, base):
        super(UnitWrapper, self).__init__(base)

        self.claimed = False
        self.owner = None
        self.name = get_first_name()
        # I need to set this field so I can track morphs
        self.unit_type = base.getType()
        self.unit_player = base.getPlayer()

        self.dead = False

        self.complete_callback = None
        self.morph_callback = None
        self.destroy_callback = None
        self.workers = []

    def abandon(self):
        self.complete_callback = None
        self.morph_callback = None
        self.destroy_callback = None
        self.owner = None
        self.claimed = False


