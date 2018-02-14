import sys
import os

# Add Lib files to jython python path
bot_folder = os.path.join(os.getenv('BOT_DIR'), os.getenv('BOT_NAME'), "AI")
bot_lib_folder = os.path.join(bot_folder, 'Lib')
sys.path.append(bot_lib_folder)


#sys.path.append('z:/app/pysrc')
sys.path.append(os.path.join(bot_folder, 'pysrc'))
import pydevd
pydevd.settrace('172.17.0.1')

#print sys.path
from bot import test_bot
from bwapi import DefaultBWListener
from bwapi import Mirror

test_bot()
print "Hello World"
