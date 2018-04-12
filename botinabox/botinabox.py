import os
import sys
import discord
import asyncio
import random
import re
import threading
import datetime
import wikipedia

client = discord.Client()

inputThread = None
channels = []
logChannel = None
users = []

class userClass:
    
    #Functions
    def __init__(self, userid,userroles,userpoints):
      self.id = userid
      self.roles = userroles
      self.points = userpoints


class InputThread(threading.Thread):
    def run(self):
        
        while True:
            self.last_user_input = input()
            print("CONSOLE: " + self.last_user_input)
            if self.last_user_input == "exit" or self.last_user_input == "close" or self.last_user_input == "quit" or self.last_user_input == "q":
                closeProg()


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
            if channel.name == "logs":
                global logChannel
                logChannel = channel
                break
    print("LOGGING CHANNEL: " + logChannel.name + ", ID: " + logChannel.id)
    print("Loaded " + str(load()) + " user profiles!")
    inputThread = InputThread()
    inputThread.daemon = True
    inputThread.start()


@client.event
async def on_message(message):
    #Ignore the bot's own messages
    if message.author.id == client.user.id:
        return

    #Log message:
    timeStamp = message.timestamp.strftime("%m/%d/%y %H:%M:%S")
    logString = timeStamp + " " + message.channel.mention + " - " + message.author.name + ": " + message.content

    #If this message is not bot's, and not in the log channel
    if message.channel.id != logChannel.id:
        print(logString)
        await client.send_message(logChannel,logString)

    try:
        #COMMANDS
        #General Commands
        if message.content.startswith('!help'):
            helpText = readFile("resources/doc.txt")
            await client.send_message(message.channel, helpText)
        elif message.content.startswith('!purge'):
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
        elif message.content.startswith('!random'):
            strings = message.content.split()
            if len(strings) < 3 or not isInt(strings[1]) or not isInt(strings[2]):
                await client.send_message(message.channel, "`Usage: !random <low> <high>`")
                return
            randNum = str(randNumGen(int(strings[1]), int(strings[2])))
            await client.send_message(message.channel, "*Your random number is:* " + randNum)
        elif message.content.startswith('!restart'):
            if os.name == 'nt':
                await client.send_message(message.channel, "*Sorry, I'm running in a DEV Environment right now and can't be restarted by command!\nTalk to wolfinabox if this comes up frequently.*")
            else:
                await client.send_message(message.channel, "*Restarting... See you soon!*")
                restart_program()
        elif message.content.startswith('!choose'):
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
        elif message.content.startswith('!allstats'):
            messageString = "**Found " + str(len(users)) + " users:**\n"
            for user in users:
                userinfo = await client.get_user_info(user.id)
                messageString +="**Name:** \"" + userinfo.name + "\", **ID:** " + user.id + "\n**Roles:** " + user.roles + ", **Points:** " + user.points + "\n"
            await client.send_message(message.channel, messageString)
        elif message.content.startswith('!stats'):
            userinfo = message.author
            user = None
            for curUser in users:
                if curUser.id == userinfo.id:
                    user = curUser
                    break
            messageString = "**Name:** \"" + userinfo.name + "\", **ID:** " + user.id + "\n**Roles:** " + user.roles + ", **Points:** " + user.points + "\n"
            await client.send_message(message.channel, messageString)
        elif message.content.startswith('!motd'):
            motdText = readFile("resources/motd.txt")
            await client.send_message(message.channel, motdText)
        #Other Hooks
        elif message.content.startswith('!wiki'):
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
            messagetext=""
            page=None
            #Error Handling
            try:
                #Get page
                page = wikipedia.page(query)
                messageText = "***" + page.title + ":***\n" + page.url + "\n`" + page.summary + "`\n"

            except wikipedia.exceptions.DisambiguationError as e:
                options=""
                for option in e.options:
                    options+=(option+'\n')
                messageText="*Sorry, be a bit more specific? I found all these things:*\n`"+options+"`"
            except wikipedia.exceptions.PageError as e:
                messageText="*Sorry, I can't find anything for \""+query+"\" on Wikipedia*."
                
            #Truncate message
            max_chars = 1000
            messageText = (messageText[:(max_chars - 4)] + '...`')if len(messageText) > max_chars else messageText
            await client.send_message(message.channel, messageText)

        #Point Commands
        elif message.content.startswith('!add'):
            True 
    except Exception as e:
        error = e
        print("ERROR ENCOUNTERED: COMMAND:{"+message.content+"},ERROR:{"+(str(error))+"}")
        await client.send_message(message.channel, "***Sorry, something's gone wrong!***\n *If this keeps happening, let wolfinabox know that the following error occured:*\n`"+"COMMAND:{"+message.content+"},ERROR:{"+(str(error))+"}`")



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
    usersFile = open("resources/stats.txt","w+")
    for user in users:
        saveString = user.id + "," + user.roles + "," + user.points
        usersFile.write(saveString)
    usersFile.close()

def load():
    global users
    numUsers = 0
    usersFile = open("resources/stats.txt")
    line = usersFile.readline()
    while line:
        parts = line.split(',')
        users.append(userClass(parts[0],parts[1],parts[2]))
        line = usersFile.readline()
        numUsers+=1
    usersFile.close()
    return numUsers

def stringOps(string):
    string = string.replace('$date$',datetime.datetime.now().strftime("%m/%d/%Y"))
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
    python = sys.executable
    os.execl(python, python, * sys.argv)

def closeProg():
    save()
    sys.exit()

client.run('NDMzMzg1MDQxNTYxNjQ5MTUz.Da7E3g.k9qnxY-onBYU3HdTP3Kta78w1Aw')
