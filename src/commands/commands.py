import asyncio
import datetime, time
from functools import partial
import random
import os
from bisect import bisect_left
import socket
import sys
import math
import numpy as np
from subprocess import call

from bs4 import BeautifulSoup

import discord
from random import randint
import urllib.request

from src.commands.customcommand import *
from src.storageclasses.serverclass import *
from src.utils.bGlobals import *
from src.utils.utils import *

import wikipedia

from warnings import catch_warnings
from builtins import int


# CLASSES===========================#
class Reminder():

    def __init__(self, client, origMessage, msg, time):
        self.origMessage = origMessage
        self.msg = msg
        self.time = time
        self.client = client

    async def run(self):
        await self.client.send_message(self.origMessage.channel, 'Okay, in ' + str(self.time) + ' seconds, I will remind you.')
        await asyncio.sleep(self.time)
        await self.client.send_message(self.origMessage.channel, self.origMessage.author.mention + ': ' + self.msg)
        
    async def schedule(self):
        await asyncio.sleep(self.time)
        await commHentai(self.origMessage.channel, client, **kwargs)
        await commScheduleHentai(message, client)


# COMMANDS==========================#
commandDict = {}


# GENERAL COMMANDS==================#
async def commTest(message, client, **kwargs):
    await client.send_message(message.channel, 'Hello there ' + message.author.name + '!')


commandDict['test'] = {'function':partial(commTest), 'usage':'A test command.', 'type':'general'}


#==================================#
async def commHelp(message, client, sClass, **kwargs):
    strings = message.content.split(None, 1)
    helptext = stringOps(data=defaultHelpText, sClass=sClass)
    msg = ""
    if len(strings) < 2:
        msg = helptext
    else:
        searchText = strings[1].strip()
        for comm, usage['usage'] in usages.items():
            if searchText in comm or searchText in usage:
                msg += '*' + comm.replace(searchText, '__' + searchText + '__') + '* ' + usage.replace(searchText, '__' + searchText + '__') + '\n'
        if not msg:
            msg = 'No results in helptext containing "' + searchText + '"'
    await client.send_message(message.channel, msg)


commandDict['help'] = {'function':partial(commHelp), 'usage':'**<search text>**Displays the helptext. Optionally, search helptext for keyword', 'type':'general'}


#==================================#
async def commRandom(message, client, **kwargs):
    formats = ['I choose number **{0}**!', '**{0}** seems good.', 'Hmmm... What about **{0}**?', 'RANDOM_NUMBER_CHOSEN: #**{0}** (beep boop)']
    strings = message.content.split()
    if len(strings) < 3 or not isInt(strings[1]) or not isInt(strings[2]):
        raise CommUsage(strings[0])
    randNum = random.randint(int(strings[1]), int(strings[2]))
    msg = random.choice(formats).format(str(randNum))
    await client.send_message(message.channel, msg)


commandDict['random'] = {'function':partial(commRandom), 'usage':'**<high> <low>** Generate a random number between high and low', 'type':'general'}

#==================================#
async def commCam(message, client, **kwargs):
    os.system("fswebcam -r 1280 /home/zootzoot/Pictures/out.jpg")
    time.sleep(1)
    await client.send_file(message.channel, "/home/zootzoot/Pictures/out.jpg")

commandDict['cam'] = {'function':partial(commCam), 'usage':'output cam', 'type':'general'}





#==================================#
async def commChoose(message, client, **kwargs):
    formats = ['I pick "{0}"!', '"{0}" seems good.', 'Hmmm... What about "{0}"?', 'RANDOM_OPTION_CHOSEN: "{0}" (beep boop)']
    strings = message.content.split(None, 1)
    if len(strings) < 2:
        raise CommUsage(strings[0])
    options = strings[1].split('|')
    if len(options) < 1:
        raise CommUsage(strings[0])
    choice = random.choice(options)
    msg = random.choice(formats).format(choice)
    await client.send_message(message.channel, msg)


commandDict['choose'] = {'function':partial(commChoose), 'usage':'**<choice1|choice2|choice3|...>** Chooses randomly from the given options', 'type':'general'}


#==================================#
async def commServerStats(message, client, server, **kwargs):
    msg = '**Stats for ' + server.name + ':**\n'
    numUsers = 0
    numBots = 0
    for member in server.members:
        if member.bot: numBots += 1
        else: numUsers += 1
    totalUsers = numUsers + numBots
    msg += '*Total Users:* ' + str(totalUsers) + '\n*Humans:* ' + str(numUsers) + '\n*Bots:* ' + str(numBots)
    await client.send_message(message.channel, msg)


commandDict['serverstats'] = {'function':partial(commServerStats), 'usage':'Get some stats on this server', 'type':'general'}


#==================================#
async def commRemind(message, client, **kwargs):
    strings = message.content.split()
    if len(strings) < 3 or not isInt(strings[1]):
        raise CommUsage(strings[0])
    remindTime = timeToSec(strings[1])
    msg = ' '.join(strings[2::])
    rmd = Reminder(client, message, msg, remindTime)
    await rmd.run()


commandDict['remindme'] = {'function':partial(commRemind), 'usage':'**<time h\:m\:s> <message>** Send a reminder after the given time', 'type':'general'}


#==================================#

async def commScheduleHentai(message, client, **kwargs):
    strings = message.content.split()
    if len(strings) < 3 or not isInt(strings[1]):
        raise CommUsage(strings[0])
    remindTime = timeToSec(strings[1])
    msg = ' '.join(strings[2::])
    rmd = Reminder(client, message, msg, remindTime)
    await rmd.schedule()


commandDict['nsfw'] = {'function':partial(commScheduleHentai), 'usage':'**<time h\:m\:s> <message>** Send a reminder after the gives', 'type':'general'}


#==================================#
async def commWiki(message, client, **kwargs):
    # Split up Strings
    strings = message.content.split()
    if len(strings) < 2:
        raise CommUsage(strings[0])
        return
    del strings[0]
    query = ' '.join(strings)
    print('Wiki query: ' + query)
    messagetext = ""
    page = None
    # Error Handling
    try:
        # Get page
        page = wikipedia.page(query)
        messageText = "***" + page.title + ":***\n" + page.url + "\n`" + page.summary + "`\n"
    except wikipedia.exceptions.DisambiguationError as e:
        options = ""
        for option in e.options:
            options += (option + '\n')
        messageText = "*Sorry, be a bit more specific? I found all these things:*\n`" + options + "`"
    except wikipedia.exceptions.PageError as e:
        messageText = "*Sorry, I can't find anything for \"" + query + "\" on Wikipedia*."
    # Truncate message
    messageText = truncate(messageText, 1000, '...`')
    await client.send_message(message.channel, messageText)


commandDict['wiki'] = {'function':partial(commWiki), 'usage':'**<thing>** Search something up on wikipedia', 'type':'general'}


#==================================#
async def commInvite(message, client, server, **kwargs):
    # Check to see if bot has already made an invite
    serverInvites = await client.invites_from(server)
    myInvite = None
    for inv in serverInvites:
        if inv.inviter == client.user and inv.max_age == 0 and not inv.revoked:
            myInvite = inv
            break
    if myInvite is None:
        myInvite = await client.create_invite(destination=message.channel, max_age=0, max_uses=0, temporary=False, unique=True)
    await client.send_message(message.channel, 'Invite: ' + myInvite.url)


commandDict['invite'] = {'function':partial(commInvite), 'usage':'Get an invite to this server', 'type':'general'}


#==================================#
async def commBotInvite(message, client, **kwargs):
    permissions = '8'
    invite = 'https://discordapp.com/oauth2/authorize?client_id=' + client.user.id + '&scope=bot&permissions=' + permissions
    await client.send_message(message.channel, 'You can use this link to add me to your server!\n' + invite)


commandDict['botinvite'] = {'function':partial(commBotInvite), 'usage':'Get a link to add this bot to your server', 'type':'general'}


#==================================#
async def commSomeone(message, client, server, **kwargs):
    formats = ['*{0}, I choose you!*', '*Hmmm... I pick {0}*', '*{0} has been chosen*']
    randomUser = random.choice(list(server.members))
    await client.send_message(message.channel, random.choice(formats).format(randomUser.mention))


commandDict['someone'] = {'function':partial(commSomeone), 'usage':'Mention someone at random', 'type':'general'}



#==================================#
async def commHentai(message, client, server, **kwargs):
    
    
   
    henid = randint(100, 748000)
    print(henid)
    location:str=os.path.join(script_dir, '/research/')
    researchLocation = script_dir.split("/utils",1)[0] + "/research/"
    try:
        researchData = np.loadtxt(researchLocation + 'researchData.txt')
    except OSError:
        open(researchLocation + 'researchData.txt', 'a').close()
    with open(researchLocation + 'researchData.txt', 'r') as f:
        data = np.genfromtxt(f,comments="!",dtype=int   )
    
    
    
    while True :
        henid = randint(100, 748000)
        print("Henid: "+ str(henid))
        opener = urllib.request.build_opener()
        request = urllib.request.Request("https://xbooru.com/index.php?page=post&s=view&id=" + str(henid))
        
        u = opener.open(request)
        print(u.geturl())
        url = "https://xbooru.com/index.php?page=post&s=view&id=" + str(henid)
        if u.geturl() == url:
           if binary_search(data,henid) == False:
               break
            
        
    
    newRow = [henid]
    data = np.concatenate((data,np.array(newRow)))
    print(data)
    data = np.sort(data, axis=None,kind='mergesort' )
    print(data)
    np.savetxt(researchLocation + 'researchData.txt',data)
    html = urllib.request.urlopen("https://xbooru.com/index.php?page=post&s=view&id=" + str(henid))
    soup = BeautifulSoup(html)
    matches = soup.findAll('img',{"src":True})
    print (matches)
    match = str(matches)
    match = match.split('https://img.xbooru.com',1)[1]
    match = match.split('?',1)[0]
    match = 'https://img.xbooru.com' + match
    print (match)
    fileis = match.split('/')[-1]
    urllib.request.urlretrieve(match, researchLocation + str(henid) + '.' + match.split('.')[-1])
    
   
    print(researchLocation)
    with open(researchLocation + str(henid) + '.' + match.split('.')[-1] , 'rb') as picture:
     await client.send_file(message.channel,picture, filename=None, content=None, tts=False)
     
commandDict['nsfw'] = {'function':partial(commHentai), 'usage':'Warning! NSFW!', 'type':'general'}


#==================================#

async def commLights(message, client, server, **kwargs):
    strings = message.content.split()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.settimeout(10)
    try:
        if 'on' in strings:
            print("Trying Lights On")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.1.27", 21))
            sock.send('RON'.encode())
            sock.send('LON'.encode())
            sock.close()
            await client.send_message(message.channel, "Let there be light!")
        elif 'off' in strings:
            print("Trying Lights Off")
            sock.connect(("192.168.1.27", 21))
            sock.send('ROFF'.encode())
            sock.send('LOFF'.encode())
            sock.close()
            await client.send_message(message.channel,
                                       "Ah you think darkness is your ally? You merely adopted the dark. I was born in it, molded by it. I didn't see the light until I was already a man, by then it was nothing to me but blinding! ")
        else:
            x = 0
            y = 40
            sock.connect(("192.168.1.27", 21))
            while True:
                 if y < 1:
                     break
            
                 on_cmd = ""
                 off_cmd = ""
        
                 if y%2:
                     on_cmd = "RON\0"
                     off_cmd = "ROFF\0"
                 else:
                     on_cmd = "LON\0"
                     off_cmd = "LOFF\0"
        
                
                 sock.send(on_cmd.encode())
                 time.sleep(abs(math.cos(x))*.1)
                 sock.send(off_cmd.encode())
                 x = x + math.pi/4
                 y = y - 1
            sock.close()
            await client.send_message(message.channel, "Notice me!")    
    except socket.timeout:
        await client.send_message(message.channel, "UwU, Are the lights disconnected?")  
    except ConnectionAbortedError:
        await client.send_message(message.channel, "UwU, Are the lights disconnected?") 
    
     
commandDict['lights'] = {'function':partial(commLights), 'usage':'lights on', 'type':'general'}


#==================================#

# ADMIN COMMANDS====================#
async def commPurge(message, client, **kwargs):
    strings = message.content.split()
    if not hasPerm(message.author, 'manage_messages', message.channel):
        raise NoPerm(strings[0])
    if len(strings) < 2 or not isInt(strings[1]):
        raise CommUsage(strings[0])
    delNum = int(strings[1]) + 1
    if delNum > 100:
        delNum = 100
    msgs = []
    async for msg in client.logs_from(message.channel, limit=delNum):
        msgs.append(msg)
    await client.delete_messages(msgs)


commandDict['purge'] = {'function':partial(commPurge), 'usage':
'**<number_of_messages>** Purge (delete) the number of messages specified in the current channel {Requires "manage_messages"}', 'type':'admin'}


#==================================#
async def commCommPrefix(message, client, sClass, **kwargs):
    strings = message.content.split()
    if not hasPerm(message.author, 'manage_server', message.channel):
        raise NoPerm(strings[0])
    if len(strings) < 2:
        raise CommUsage(strings[0])
    oldcommandPrefix = sClass.commandPrefix
    sClass.commandPrefix = strings[1].strip()
    await client.send_message(message.channel,
    'The command prefix for this server was changed from \"' + oldcommandPrefix + '\" to \"' + sClass.commandPrefix + '\".')


commandDict['commandprefix'] = {'function':partial(commCommPrefix), 'usage':
'**<character>** Change this server\'s command prefix {Requires "manage_server"}', 'type':'admin'}

async def commUpdate(message, client, sClass, **kwargs):
    strings = message.content.split()
    if not hasPerm(message.author, 'manage_server', message.channel):
        raise NoPerm(strings[0])
   
    call(['bash','/home/zootzoot/discord/botinabox/update.sh'])
    await client.send_message(message.channel,
    'Updating!')


commandDict['update'] = {'function':partial(commUpdate), 'usage':
'Updates server from git', 'type':'admin'}


#==================================#
async def commCustomCommand(message, client, sClass, **kwargs):
    strings = message.content.split()
    if not hasPerm(message.author, 'manage_server', message.channel) and (strings[1] == 'create' or strings[1] == 'delete'):
        raise NoPerm(strings[0] + ' ' + strings[1])
    if len(strings) < 2:
        raise CommUsage(strings[0])
    # Parse first argument
    if strings[1] == 'help':
        await customCommHelp(message, client, sClass)
    elif strings[1] == 'create':
        await customCommCreate(message, client, sClass)
    elif strings[1] == 'delete':
        await customCommDelete(message, client, sClass)
    elif strings[1] == 'list':
        await customCommList(message, client, sClass)


commandDict['customcommand'] = {'function':partial(commCustomCommand), 'usage':
'**<help|list|create|delete>** Manage this server\'s custom commands. See customcommand help for more info {Requires "manage_server" for creation/deletion}',
'type':'admin'}
#==================================#


def commUsages(command:str, commandPrefix:str=defaultCommandPrefix):
    usage = '`' + commandPrefix + command + '` ' + commandDict[command]['usage'] if command in commandDict.keys() else 'No information on command `' + commandPrefix + command + '` found.'
    return usage

    
def stringOps(data:str, sClass:serverClass=None, server:discord.server=None):
    # Generic replacements
    data = data.replace('$date$', datetime.now().strftime("%m/%d/%Y"))
    # Server Specific replacements
    if sClass is not None:
        data = data.replace('$allCommands$', '\n'.join([commUsages(comm, sClass.commandPrefix) for comm in commandDict.keys()]))
        data = data.replace('$generalCommands$', '**General Commands:**\n' + ('\n'.join(commUsages(comm, sClass.commandPrefix) for comm in commandDict.keys() if commandDict[comm]['type'] == 'general')))
        data = data.replace('$adminCommands$', '**Admin Commands:**\n' + ('\n'.join(commUsages(comm, sClass.commandPrefix) for comm in commandDict.keys() if commandDict[comm]['type'] == 'admin')))
    if sClass is not None:
        if sClass.customCommands:
            data = data.replace('$customCommands$', '**Custom Commands:**\n' + ('\n'.join(['`' + sClass.commandPrefix + comm + '` ' + response for comm, response in sClass.customCommands.items()])))
        else:
            data = data.replace('$customCommands$', '')
    if server is not None:
        data = data.replace('$serverName$', client.get_server(sClass.id).name)
    return data


def hasPerm(member, permission, channel):
    userPerms = dict(channel.permissions_for(member))
    return userPerms[permission]
