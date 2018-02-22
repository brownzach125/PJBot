from pubsub import pub
from decorator import decorate


class every(object):
    def __init__(self, event_name, condition=lambda **cond_kwargs: True):
        self.event_name = event_name
        self.condition = condition
    
    def __call__(self, f):
        def wrapper(f, *args, **kwargs):
            if self.condition(**kwargs):
                return f(*args, **kwargs)
        decorated_wrapper = decorate(f, wrapper)
        pub.subscribe(decorated_wrapper, self.event_name)
        return decorated_wrapper

class once(object):
    def __init__(self, event_name, condition=lambda **cond_kwargs: True):
        self.event_name = event_name
        self.condition = condition
    
    def __call__(self, f):
        def wrapper(f, *args, **kwargs):
            if self.condition(**kwargs):
                pub.unsubscribe(decorated_wrapper, self.event_name)
                return f(*args, **kwargs)
        decorated_wrapper = decorate(f, wrapper)
        pub.subscribe(decorated_wrapper, self.event_name)
        return decorated_wrapper


# just hold onto references
_schedules = []

def yield_for_events(fgen):
    """
    decorator that advances the generator function when a
    message is sent to the yielded topic if the yielded condition
    is true
    """
    def yield_wrapper(*args, **kwargs):
        gen = fgen(*args, **kwargs)
        s = __Schedule(gen, fgen.func_name)
        _schedules.append(s)
        s(*args, **kwargs)
        return s
    return yield_wrapper

class __Schedule(object):
    def __init__(self, generator, name):
        self.generator = generator
        self.name = name
        self.curr_event = None
        self.condition = lambda **kwargs: True

    def __call__(self, *args, **kwargs):
        try:
            if self.condition(**kwargs):
                if self.curr_event is None:
                    ret = self.generator.next()
                else:
                    pub.unsubscribe(self, self.curr_event)
                    ret = self.generator.send(kwargs)
                if isinstance(ret, tuple):
                    self.curr_event, self.condition = ret
                else:
                    self.curr_event, self.condition = ret, lambda **kwargs: True
                # ideally this is we would modify our signature to match
                # but we don't know what the signature is
                listen, _ =pub.subscribe(self, self.curr_event)
                # this is a better name for the Listener
                listen._ListenerBase__nameID = self.name
        except StopIteration:
            pass
