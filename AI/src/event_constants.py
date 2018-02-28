from pubsub import pub

onStart = "onStart"
onUnitCreate = "onUnitCreate"
onUnitComplete = "onUnitComplete"
onUnitMorph = "onUnitMorph"
onUnitDiscover = "onUnitDiscover"
onUnitEvade = "onUnitEvade"
onUnitShow = "onUnitShow"
onUnitHide = "onUnitHide"
onUnitDestroy = "onUnitDestroy"
onFrame = "onFrame"


def event_x_for_u(event, unit):
    return event + '.' + str(unit.getID())


def send_event_x_for_u(event, unit):
    event_name = event_x_for_u(event, unit)
    pub.sendMessage(event_name, unit=unit)
