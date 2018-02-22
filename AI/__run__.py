import sys
import os
import traceback
import time

#pysrc_folder = os.getenv('BOT_DIR') + "/" + os.getenv('BOT_NAME') + "/AI/pysrc"
#sys.path.append(pysrc_folder)
#import pydevd
#pydevd.settrace('172.17.0.1', stdoutToServer=True, stderrToServer=True, suspend=False)
sys.path.append("C:/Users/solevi/PycharmProjects/PJBot/bwmirror_v2_5.jar")
# site-packages folder
sys.path.append("./Lib/site-packages")

try:
    from Lib.bot import Bot
    # Calls mirror.start which blocks until the end of the game
    Bot().run()
except Exception as e:
    print e
    traceback.print_exc()
    


