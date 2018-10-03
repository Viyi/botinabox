import os
import sys
from src.utils.utils import *
#Util stuff
script_dir = os.path.dirname(sys.executable) if getattr(sys,'frozen',False) else os.path.join(os.path.dirname(__file__),'..')
isExecutable = getattr(sys,'frozen',False)
#Defaults
defaultCommandPrefix='&'
defaultLogChannelName='logs'
defaultHelpText="""***BotInABox Helpfile, v1.0.0***
**<=======================================================>**
$generalCommands$
$adminCommands$
$customCommands$
**<=======================================================>**"""
defaultMotd="""**/\\/\\/\\$serverName$ Message Of The Day $date$/\\/\\/\\**
**<======================================================>**
Remember to always keep as __positive__ as possible!"""