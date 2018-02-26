from bwapi import MouseButton

from pubsub import pub
from AI.src.subscribe import every
from AI.src import event_constants as event_constants
from AI.src.blackboard import BlackBoard

import logging

bb = BlackBoard()

@every(event_constants.onStart)
def on_start():
    pass

mouse_button_states = {}
mouse_buttons = [MouseButton.M_LEFT, MouseButton.M_MIDDLE, MouseButton.M_RIGHT, MouseButton.M_MAX]

@every(event_constants.onFrame)
def on_frame():
    game = bb.game
    for mouse_button in mouse_buttons:
        button_down = game.getMouseState(mouse_button)
        last_state = mouse_button_states.get(mouse_button, False)

        if button_down != last_state:
            position = game.getMousePosition()
            mouse_button_states[mouse_button] = button_down
            if button_down:
                pub.sendMessage('mouse_down.' + str(mouse_button), position=position)
                bb.mouse_down_location = position
            else:
                pub.sendMessage('mouse_up.' + str(mouse_button), position=position)
                pub.sendMessage('mouse_click.' + str(mouse_button), position=position)
                bb.mouse_up_location = position
                logging.debug('mouse_click at ' + str(position))









