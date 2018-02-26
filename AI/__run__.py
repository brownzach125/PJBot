import sys
import traceback

#pysrc_folder = os.getenv('BOT_DIR') + "/" + os.getenv('BOT_NAME') + "/AI/pysrc"
#sys.path.append(pysrc_folder)
#import pydevd
#pydevd.settrace('172.17.0.1', stdoutToServer=True, stderrToServer=True, suspend=False)
sys.path.append("C:/Users/solevi/PycharmProjects/PJBot/AI/bwmirror_v2_5.jar")
# site-packages folder
sys.path.append("./Lib/site-packages")
print sys.path


try:
    from src.bot import Bot
    # Calls mirror.start which blocks until the end of the game
    Bot().run()
except Exception as e:
    print e
    traceback.print_exc()
    


