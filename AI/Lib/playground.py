import sys
sys.path.append("C:/Users/solevi/PycharmProjects/PJBot/bwmirror_v2_5.jar")
import inspect

from bwapi import Game
from bwapi import UnitType

for key in UnitType.__dict__.keys():
    "@property\n" \
    "def " + key + "(self):\n"\
    "\treturn getattr(self._base"+ key+ ")"



    print key + " = None"

