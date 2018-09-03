from utils.bGlobals import *
class serverClass:
    def __init__(self,id):
        self.id = id
        self.commandPrefix = defaultCommandPrefix
        #self.logChannelName = defaultLogChannelName
        #self.users = {}
        self.customCommands = {}
        #self.logChannel = None