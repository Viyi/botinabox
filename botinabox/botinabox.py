import os
import sys
import discord
import asyncio
import random
import re
import threading
import datetime
import wikipedia
from difflib import SequenceMatcher
#================================================#
#===============USER SET VARIABLES===============#
#This is the character to use commands (EG: !help, &help, #help)
commandChar='&'
#This is the channel on the server to log chat to
logChannelName="logs"
#This is the client ID of the bot account you've created
clientID='id_here'
#================================================#
#================================================#


inputThread = None
channels = []
logChannel = None
users = {}
commands=[]

client = discord.Client()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class userClass:
    
    #Functions
    def __init__(self,name,userid,userpoints):
      self.name = name
      self.id = userid
      self.points = userpoints


class InputThread(threading.Thread):
    def run(self):
        
        while True:
            self.last_user_input = input()
            print("CONSOLE: " + self.last_user_input)
            if self.last_user_input == "exit" or self.last_user_input == "close" or self.last_user_input == "quit" or self.last_user_input == "q":
                closeProg()
                os._exit
                exit()
            elif self.last_user_input == "save":
                save()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #Find log channel
    global channels
    channels = client.get_all_channels()
    for channel in channels:
            #print(channel.name+", ID: "+channel.id);
            if channel.name == logChannelName:
                global logChannel
                logChannel = channel
                break
    print("LOGGING CHANNEL: " + logChannel.name + ", ID: " + logChannel.id)
    print("Loaded " + str(load()) + " existing users!")
    global inputThread
    inputThread = InputThread()
    inputThread.daemon = True
    inputThread.start()
    loadCommands()
    print("Loaded commands: "+'[%s]' % ', '.join(map(str, commands)))


@client.event
async def on_message(message):
    #Ignore the bot's own messages
    if message.author.id == client.user.id:
        return

    #Log message:
    timeStamp = message.timestamp.strftime("%m/%d/%y %H:%M:%S")
    logString = "`" + timeStamp + " " + message.channel.mention + " - " + message.author.name + ": " + message.content + "`"

    #If this message is not bot's, and not in the log channel
    if message.channel.id != logChannel.id:
        print(logString)
        await client.send_message(logChannel,logString)

    try:
        #COMMANDS
        #General Commands
        if message.content.startswith(commandChar+'help'):
            helpText = readFile("resources/doc.txt")
            await client.send_message(message.channel, helpText)
        elif message.content.startswith(commandChar+'purge'):
            strings = message.content.split()
            if len(strings) < 2 or not isInt(strings[1]):
                await client.send_message(message.channel, "`Usage: !purge <num of msgs> `")
                return
            delNum = int(strings[1]) + 1
            if delNum > 100:
                delNum = 100
        
            msgs = []
            async for x in client.logs_from(message.channel, limit=delNum):
                msgs.append(x)
            await client.delete_messages(msgs)
        elif message.content.startswith(commandChar+'random'):
            strings = message.content.split()
            if len(strings) < 3 or not isInt(strings[1]) or not isInt(strings[2]):
                await client.send_message(message.channel, "`Usage: !random <low> <high>`")
                return
            randNum = str(randNumGen(int(strings[1]), int(strings[2])))
            await client.send_message(message.channel, "*Your random number is:* " + randNum)
        elif message.content.startswith(commandChar+'restart'):
            if os.name == 'nt':
                await client.send_message(message.channel, "*Sorry, I'm running in a DEV Environment right now and can't be restarted by command!\nTalk to wolfinabox if this comes up frequently.*")
            else:
                await client.send_message(message.channel, "*Restarting... See you soon!*")
                restart_program()
        elif message.content.startswith(commandChar+'choose'):
            strings = message.content.split(None,1)
            if len(strings) < 2:
                await client.send_message(message.channel, "`Usage: !choose <option1|option2|option3|...> `")
                return
            options = strings[1].split('|')
            if len(options) < 1:
                await client.send_message(message.channel, "1I need at least one thing to choose from, silly!1")
    
                return
            choice = random.choice(options)
            await client.send_message(message.channel, "*I choose: \"" + choice + "\"*")
        elif message.content.startswith(commandChar+'allstats'):
            messageText = "**Found " + str(len(users)) + " Users:**\n"
            #Iterate through users, adding their stats to the string
            for userKey, userVal in users.items():
                messageText+=getUserStats(userKey)
            #Trucate if necessary (TEMPORARY)
            max_chars = 1000
            messageText = (messageText[:(max_chars - 4)] + '...`')if len(messageText) > max_chars else messageText
            await client.send_message(message.channel, messageText)
        elif message.content.startswith(commandChar+'stats'):
            id = message.author.id
            messageString = getUserStats(id)
            await client.send_message(message.channel, messageString)
        elif message.content.startswith(commandChar+'motd'):
            motdText = readFile("resources/motd.txt")
            await client.send_message(message.channel, motdText)

        #Other Hooks
        elif message.content.startswith(commandChar+'wiki'):
            #Split up Strings
            strings = message.content.split()
            if len(strings) < 2:
                await client.send_message(message.channel, "`Usage: !wiki <thing>`")
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

        #Point Commands
        elif message.content.startswith(commandChar+'add'):
            strings = message.content.split()
            if len(strings) < 2 or not (isInt(strings[1]) or isInt(strings[2])):
                await client.send_message(message.channel, "`Usage: !add <# of points> @user `")
                return
            
            amount = None
            if isInt(strings[1]): 
                amount = int(strings[1])
            else: 
                amount = int(strings[2])
            userID = str(message.mentions[0].id)

            #Set Points
            users[userID].points = str(int(users[userID].points) + amount)


        #Command not recognised
        elif message.content.startswith(commandChar):
            messageText=""
            strings = message.content.split()
            commandsDict={}
            #Set percent likelyhood of each command
            for string in commands:
                percent=int(similar(strings[0],string)*100)
                while percent in commandsDict.keys():
                    percent+=1
                commandsDict[percent]=string
            #commandsDict=sorted(commandsDict,key=commandsDict.get)
            mostLikelyPercent=max(k for k, v in  commandsDict.items())
            mostLikelyString=commandsDict[mostLikelyPercent]
            messageText+="*Sorry, I don't recognise \""+strings[0]+"\"*\n"
            if (mostLikelyPercent>40):
                messageText+="*Did you mean:*\n"
                for key in reversed(sorted(commandsDict)):
                   if (key>40):
                         messageText+="*("+str(key)+"%)* `"+commandsDict[key]+"`\n"
            
            await client.send_message(message.channel, messageText)


    #Exceptions
    except Exception as e:
        error = e
        print("ERROR ENCOUNTERED: COMMAND:{" + message.content + "},ERROR:{" + (str(error)) + "}")
        await client.send_message(message.channel, "***Sorry, something's gone wrong!***\n *If this keeps happening, let wolfinabox know that the following error occured:*\n`" + "COMMAND:{" + message.content + "},ERROR:{" + (str(error)) + "}`")

def getUserStats(id):
    userC = users[id]
    return ("**Name:** \"" + userC.name + "\", **ID:** " + userC.id + ", **Points:** " + userC.points + "\n")

def randNumGen(high, low):
    random.seed()
    return random.randint(high, low)

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def save():
    print("Saving " + str(len(users)) + " users...\n")
    usersFile = open("resources/stats.txt","w+")
    for userKey,userValue in users.items():
        saveString = userValue.name + "," + userValue.id + "," + userValue.points
        usersFile.write(saveString + '\n')
    usersFile.close()
    print("Saving complete!\n")

def load():
    global users
    #Load Existing Users
    numUsers = 0
    usersFile = open("resources/stats.txt")
    line = usersFile.readline()
    while line:
        line = line.strip()
        if line.isspace(): continue
        parts = line.split(',')
        users[parts[1]] = (userClass(parts[0],parts[1],parts[2]))
        line = usersFile.readline()
        numUsers+=1
    usersFile.close()

    #Create new users
    for user in client.get_all_members():
        if user.id not in users:
            users[user.id] = (userClass(user.name,user.id,'1000'))
            print("Created Entry for User: " + user.name + ", ID: " + user.id + "\n")
    return numUsers

def stringOps(string):
    string = string.replace('$date$',datetime.datetime.now().strftime("%m/%d/%Y"))
    string = string.replace('$commandChar$',commandChar)

    return string

def readFile(fileName):
    file = open(fileName)
    returnString = ""
    line = file.readline()
    while line:
           line = stringOps(line)
           returnString+=(line)
           line = file.readline()
    return returnString

def restart_program():
    save()
    python = sys.executable
    os.execl(python, python, * sys.argv)

def loadCommands():
     file = open("resources/doc.txt")
     global commands
     for line in file.readlines():
            if '`' in line: commands.append(stringOps(line.split("`", 1)[1].split("`", 1)[0]))

def closeProg():
    save()

client.run(clientID)
