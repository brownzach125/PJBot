import sys
import os

pysrc_folder = os.getenv('BOT_DIR') + "/" + os.getenv('BOT_NAME') + "/AI/pysrc"
sys.path.append(pysrc_folder)
import pydevd
pydevd.settrace('172.17.0.1', stdoutToServer=True, stderrToServer=True)

from Lib.bot import Bot

Bot().run()

