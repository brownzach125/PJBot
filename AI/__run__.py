print "a"
import sys
import os
import traceback
import time

print "A"
pysrc_folder = os.getenv('BOT_DIR') + "/" + os.getenv('BOT_NAME') + "/AI/pysrc"
sys.path.append(pysrc_folder)
import pydevd
print "B"
pydevd.settrace('172.17.0.1', stdoutToServer=True, stderrToServer=True, suspend=False)
print "Python path"
print sys.path

try:
    from Lib.bot import Bot
    # Calls mirror.start which blocks until the end of the game
    Bot().run()
except Exception as e:
    print e
    traceback.print_exc()
    


