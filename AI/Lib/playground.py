import sys
sys.path.append("C:/Users/solevi/PycharmProjects/PJBot/bwmirror_v2_5.jar")
from bwapi import UnitType
from blackboard import BlackBoard
from playground2 import func


import threading

def worker():
    import time
    bb = BlackBoard()
    time.sleep(5)
    print bb.free_units
    print bb.game
    return


#threading.Thread(target=worker).start()
def foo():
    bb = BlackBoard()
    bb.game = 42
    bb.free_units[1] = 10
foo()

func()



