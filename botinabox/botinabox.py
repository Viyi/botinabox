import os #For exit and such
import sys #For restart
import discord #For obvious reasons
import asyncio #Needed for discord
import random #For the RNG generators
import re #Don't remember
import threading #For the input thread
import datetime #For getting the date and time
import wikipedia #For the wiki command
from difflib import SequenceMatcher #For the command suggestions

#================================================#
#===============USER SET VARIABLES===============#
#This is the character to use commands (EG: !help, &help, #help)
defaultCommandChar = '&'
#This is the channel on the server to log chat to
defaultLogChannelName = "logs"
#This is the default admin role, that can change bot settings
defaultAdminRole='admin'
#Time, in seconds, between autosaves (saves all server/user settings to file)
autoSaveTime=300
#This is the client ID of the bot account
clientID = 'id_here'
#This determines whether or not to log /all/ messages from /all/ servers to the console.
#Not recommended if the bot is active on many large servers
logAllMessagesToConsole=True
#================================================#
#================================================#
#DEFAULTS
defaultHelpText = """***BotInABox Helpfile, v0.0.6***
**<=======================================================>**
`$commandChar$help` - See this helpfile
`$commandChar$purge` **<amount>** Purge (delete) the number of messages specified in the current channel
`$commandChar$random` **<high> <low>** Generate a random number between high and low
`$commandChar$choose` **<choice1|choice2|choice3|...>** Chooses randomly from the given options
`$commandChar$remindme` **<seconds> <message>** Set a reminder that will notify you after the given amount of seconds, with the given message.
`$commandChar$motd` Show the current *"message of the day"*
`$commandChar$stats` Prints in stats for the user requesting
`$commandChar$allstats` Prints stats for every user on the server
`$commandChar$wiki` **<thing>** Search something up on wikipedia!
**<=======================================================>**"""

defaultMotd = """**/\\/\\/\\$serverName$ Message Of The Day $date$/\\/\\/\\**
**<======================================================>**
Remember to always keep as __positive__ as you can!"""
#END DEFAULTS

#GLOBAL VARIABLES
inputThread = None #The thread for console input
client = discord.Client()
classServers = {}
#END GLOBAL VARIABLES

#CLASSES
#The class to store "non-discord" (points, etc) info about a user
class userClass:
      def __init__(self,name,userid,userpoints):
        self.name = name
        self.id = userid
        self.points = userpoints

#The class to store info about a server
class serverClass:
    def __init__(self,id):
        self.id = id
        self.commandChar = defaultCommandChar
        self.logChannelName = defaultLogChannelName
        self.adminRole=defaultAdminRole
        self.users = {}
        self.commands = []
        self.logChannel=None

#The class that runs the console input in a separate thread
class InputThread(threading.Thread):
    def run(self):
        
        while True:
            self.last_user_input = input()
            print("CONSOLE: " + self.last_user_input)
            if self.last_user_input == "exit" or self.last_user_input == "close" or self.last_user_input == "quit" or self.last_user_input == "q":
                #closeProg()
                #os._exit
                #exit()
                True
            elif self.last_user_input == "save":
                save()
                True
#END CLASSES

#FUNCTIONS
#Utility
def loadID():
    try:
        file=open('token.txt')
        loaded_id= file.readline()
        global clientID
        clientID=loaded_id 
    except FileNotFoundError:
        return

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def randNumGen(high, low):
    random.seed()
    return random.randint(high, low)

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def stringOps(string, classServer):
    string = string.replace('$date$',datetime.datetime.now().strftime("%m/%d/%Y"))
    string = string.replace('$commandChar$',classServer.commandChar)
    string = string.replace('$serverName$',client.get_server(classServer.id).name)
    return string

def readFile(fileName,classServer):
    file = open(fileName)
    returnString = ""
    line = file.readline()
    while line:
           line = stringOps(line,classServer)
           returnString+=(line)
           line = file.readline()
    return returnString

#Initialise a new serverClass
def initServer(serverID):
    server = client.get_server(serverID)
    classServers[serverID] = (serverClass(serverID))
    #Initialise members
    for user in server.members:
        if user.id not in classServers[serverID].users:
            classServers[serverID].users[user.id] = (userClass(user.name,user.id,'1000'))
            print("Created Entry for User: " + user.name + ", ID: " + user.id + "")
    print('Created ' + str(len(classServers[serverID].users)) + ' users')
    #Initialise command suggestions from default helptext
    commandLines = defaultHelpText.split('\n')
    for line in commandLines:
        if '`' in line: classServers[serverID].commands.append(stringOps(line.split("`", 1)[1].split("`", 1)[0],classServers[serverID]))

#Save/Load
def autosave():
    threading.Timer(300.0, autosave).start()
    print("Autosaving...")
    save()

def save():
    for serverKey,serverValue in classServers.items():
        saveServer(serverKey)
        print('<=======================>')

def saveServer(serverID):
    server=classServers[serverID]
    print('Saving Server: '+client.get_server(serverID).name+', ID: '+str(serverID))
    path=r'./resources/servers/'+serverID
    #Make folder if necessary
    if not os.path.exists(path):
        print('Creating directory '+path)
        os.makedirs(path)
    #Save Files
    #Users file
    usersFile = open(path+"/users.txt","w+")
    print("Saving " + str(len(server.users)) + " users")
    for userKey,userValue in server.users.items():
       saveString = userValue.name + "," + userValue.id + "," + userValue.points
       usersFile.write(saveString + '\n')
    usersFile.close()

    #Motd file
    if not os.path.exists(path+"/motd.txt"):
        motdFile=open(path+"/motd.txt", "w+")
        print("Saving default MOTD File")
        motdFile.write(defaultMotd)
        motdFile.close()

    #Helptext file
    #if not os.path.exists(path+"/doc.txt"):
    #For now, we need to save over the helptext file.
    #In the future, servers will be able to have their own custom helptexts.
    docFile=open(path+"/doc.txt", "w+")
    print("Saving default doc File")
    docFile.write(defaultHelpText)
    docFile.close()

    #Settings file
    settingsFile=open(path+"/settings.txt","w+")
    print("Saving settings")
    settingsFile.write(server.commandChar+'\n')
    settingsFile.write(server.logChannelName+'\n')
    settingsFile.write(server.adminRole+'\n')

def loadServer(serverID):
    server = client.get_server(serverID)
    #If the server folder doesn't exist already
    path='./resources/servers/'+serverID
    if not os.path.exists(path):
        print("Creating new entry for "+server.name)
        initServer(serverID)
        return
    #Otherwise, load it from files.
    print("Loading "+server.name)
    classServers[serverID] = (serverClass(serverID))
    
    #Load Settings
    settingsFile=open(path+"/settings.txt")
    classServers[serverID].commandChar=settingsFile.readline().strip()
    classServers[serverID].logChannelName=settingsFile.readline().strip()
    classServers[serverID].adminRole=settingsFile.readline().strip()
    settingsFile.close()

    #Load Commands
    helpTextFile=open(path+'/doc.txt')
    for line in helpTextFile.readlines():
        if '`' in line: classServers[serverID].commands.append(stringOps(line.split("`", 1)[1].split("`", 1)[0],classServers[serverID]).strip())
    helpTextFile.close()

    #Load Users
    usersFile=open(path+'/users.txt')
    for line in usersFile.readlines():
        line=line.strip()
        if line.isspace(): continue
        parts=line.split(',')
        classServers[serverID].users[parts[1]] = (userClass(parts[0],parts[1],parts[2]))
    usersFile.close()

    #Create New Users
    for user in server.members:
        if user.id not in classServers[serverID].users:
            classServers[serverID].users[user.id] = (userClass(user.name,user.id,'1000'))
            print("Created Entry for User: " + user.name + ", ID: " + user.id + "")
    print('Loaded/Created ' + str(len(classServers[serverID].users)) + ' users')


#Message-related Functions
async def remind(time,originalMessage,message):
    await asyncio.sleep(time)
    print('Reminding: '+message)
    await client.send_message(originalMessage.channel,'*Reminder: <@'+originalMessage.author.id+'>:* '+message)

def getUserStats(serverID,userID):
    userC = classServers[serverID].users[userID]
    return ("**Name:** \"" + userC.name + "\", **ID:** " + userC.id + ", **Points:** " + userC.points + "\n")

#END FUNCTIONS

#DISCORD CODE
@client.event
async def on_ready():
    #Header Info
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #Input Thread
    global inputThread
    inputThread = InputThread()
    inputThread.daemon = True
    inputThread.start()
    
    #Servers
    print('Joined ' + str(len(list(client.servers))) + ' servers:')
    print('<=======================>')
    for server in client.servers:
        print('Name: \"' + server.name + '\", ID: ' + server.id + ', Members: ' + str(len(list(server.members))) + ', Large: ' + str(server.large))
        loadServer(server.id)
        print("Loaded " + str(len(classServers[server.id].commands)) + " commands: " + '[%s]' % ', '.join(map(str, classServers[server.id].commands)))
        for channel in server.channels:
            #print(channel.name+", ID: "+channel.id);
            if channel.name == classServers[server.id].logChannelName:
                classServers[server.id].logChannel = channel
                break
        print("Logging Channel: " + classServers[server.id].logChannel.name + ", ID: " + classServers[server.id].logChannel.id)

        print('<=======================>')
    autosave()

    elapsedTime = datetime.datetime.now() - startTime
    print('Bot started successfully! Took ' + str(elapsedTime.seconds) + '.' + str(elapsedTime.microseconds) + ' seconds')

@client.event
async def on_message(message):
    server=message.server
    classServer=classServers[server.id]
    path="./resources/servers/"+server.id
    #If the message belongs to the bot, ignore it
    if message.author == client.user:
        return
    #We can't handle PM's just yet, so any message with no server should be ignored.
    if server==None:
        return

    timeStamp = message.timestamp.strftime("%m/%d/%y %H:%M:%S")
    logString = "`" + timeStamp + " [" + message.channel.name + "] - " + message.author.name + ": " + message.content + "`"

    #If this message is not in the log channel
    if message.channel.id != classServer.logChannel.id:
        if logAllMessagesToConsole: print('\"'+server.name+'\" '+logString)
        await client.send_message(classServer.logChannel,logString)

    #If it mentioned everyone (a bit of cheeky fun)
    if message.mention_everyone:
        await client.send_message(message.channel,"Did you *really* have to mention everyone, <@"+message.author.id+">? Do you know how annoying that is?")
    try:
    #Reacts
    #if "botinabox" in message.content.lower():
    #    emoji=discord.utils.get(client.get_all_emojis(),name='heart')
    #    await client.add_reaction(message,emoji)

    #COMMANDS
    
        #GENERAL COMMANDS
        if message.content.startswith(classServer.commandChar + 'help'):
            helpText = readFile(path+"/doc.txt",classServer)
            await client.send_message(message.channel, helpText)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'purge'):
            strings = message.content.split()
            if len(strings) < 2 or not isInt(strings[1]):
                await client.send_message(message.channel, "`Usage: " + classServer.commandChar + "purge <num of msgs> `")
                return
            delNum = int(strings[1]) + 1
            if delNum > 100:
                delNum = 100
            msgs = []
            async for msg in client.logs_from(message.channel, limit=delNum):
                msgs.append(msg)
            await client.delete_messages(msgs)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'random'):
            strings = message.content.split()
            if len(strings) < 3 or not isInt(strings[1]) or not isInt(strings[2]):
                await client.send_message(message.channel, "`Usage: " + classServer.commandChar + "random <low> <high>`")
                return
            randNum = str(randNumGen(int(strings[1]), int(strings[2])))
            await client.send_message(message.channel, "*Your random number is:* " + randNum)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'remindme'):
            strings = message.content.split()
            if len(strings) < 2 or not isInt(strings[1]):
                await client.send_message(message.channel, "`Usage: " + classServer.commandChar + "remindme <seconds> <message>`")
                return
            reminderMessage=""
            for x in range(2,len(strings)):
                reminderMessage+=strings[x]+' '
            await remind(int(strings[1]),message,reminderMessage)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'choose'):
            strings = message.content.split(None,1)
            if len(strings) < 2:
                await client.send_message(message.channel, "`Usage: " + classServer.commandChar + "choose <option1|option2|option3|...> `")
                return
            options = strings[1].split('|')
            if len(options) < 1:
                await client.send_message(message.channel, "*I need at least one thing to choose from, silly!*")
    
                return
            choice = random.choice(options)
            await client.send_message(message.channel, "*I choose: \"" + choice + "\"*")
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'allstats'):
            messageText = "**Found " + str(len(classServer.users)) + " Users:**\n"
            #Iterate through users, adding their stats to the string
            for userKey, userVal in classServer.users.items():
                messageText+=getUserStats(classServer.id,userKey)
            #Trucate if necessary (TEMPORARY)
            max_chars = 1000
            messageText = (messageText[:(max_chars - 4)] + '...`')if len(messageText) > max_chars else messageText
            await client.send_message(message.channel, messageText)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'stats'):
            id = message.author.id
            messageString = getUserStats(classServer.id,id)
            await client.send_message(message.channel, messageString)
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'motd'):
            motdText = readFile(path+"/motd.txt",classServer)
            await client.send_message(message.channel, motdText)
        #================================================#

        #Other Hooks
        #================================================#
        elif message.content.startswith(classServer.commandChar + 'wiki'):
            #Split up Strings
            strings = message.content.split()
            if len(strings) < 2:
                await client.send_message(message.channel, "`Usage: " + classServer.commandChar + "wiki <thing>`")
                return
            del strings[0]
            query = ""
            for string in strings:
                query+=(string + " ")
            print(query)
            messagetext = ""
            page = None
            #Error Handling
            try:
                #Get page
                page = wikipedia.page(query)
                messageText = "***" + page.title + ":***\n" + page.url + "\n`" + page.summary + "`\n"

            except wikipedia.exceptions.DisambiguationError as e:
                options = ""
                for option in e.options:
                    options+=(option + '\n')
                messageText = "*Sorry, be a bit more specific? I found all these things:*\n`" + options + "`"
            except wikipedia.exceptions.PageError as e:
                messageText = "*Sorry, I can't find anything for \"" + query + "\" on Wikipedia*."
                
            #Truncate message
            max_chars = 1000
            messageText = (messageText[:(max_chars - 4)] + '...`')if len(messageText) > max_chars else messageText
            await client.send_message(message.channel, messageText)
        #================================================#
        

        #Command not recognised
        #================================================#
        elif message.content.startswith(classServer.commandChar):
            messageText = ""
            strings = message.content.split()
            commandsDict = {}
            #Set percent likelyhood of each command
            for string in classServer.commands:
                percent = int(similar(strings[0],string) * 100)
                while percent in commandsDict.keys():
                    percent+=1
                commandsDict[percent] = string
            #commandsDict=sorted(commandsDict,key=commandsDict.get)
            mostLikelyPercent = max(k for k, v in  commandsDict.items())
            mostLikelyString = commandsDict[mostLikelyPercent]
            messageText+="*Sorry, I don't recognise \"" + strings[0] + "\"*\n"
            if (mostLikelyPercent > 40):
                messageText+="*Did you mean:*\n"
                for key in reversed(sorted(commandsDict)):
                   if (key > 40):
                         messageText+="*(" + str(key) + "%)* `" + commandsDict[key] + "`\n"
            
            await client.send_message(message.channel, messageText)


    #Exceptions
    except Exception as e:
        error = e
        print("ERROR ENCOUNTERED: COMMAND:{" + message.content + "},ERROR:{" + (str(error)) + "}")
        await client.send_message(message.channel, "***Sorry, something's gone wrong!***\n *If this keeps happening, let wolfinabox know that the following error occured:*\n`" + "COMMAND:{" + message.content + "},ERROR:{" + (str(error)) + "}`")


#Start bot
startTime = datetime.datetime.now()
loadID()
client.run(clientID)
#END DISCORD CODE