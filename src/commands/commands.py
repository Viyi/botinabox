import discord
import asyncio
import random
import wikipedia
import datetime,time
from functools import partial
from src.utils.bGlobals import *
from src.utils.utils import *
from storageclasses.serverclass import *
from commands.customcommand import *
#CLASSES===========================#
class Reminder():
    def __init__(self,client,origMessage,msg,time):
        self.origMessage=origMessage
        self.msg=msg
        self.time=time
        self.client=client
    async def run(self):
        await self.client.send_message(self.origMessage.channel,'Okay, in '+str(self.time)+' seconds, I will remind you.')
        await asyncio.sleep(self.time)
        await self.client.send_message(self.origMessage.channel,self.origMessage.author.mention+': '+self.msg)

#COMMANDS==========================#
commDispatcher={}
usages={}
#GENERAL COMMANDS==================#
async def commTest(message,client,**kwargs):
    await client.send_message(message.channel,'Hello there '+message.author.name+'!')
commDispatcher['test']=partial(commTest)
usages['test']='A test command.'
#==================================#
async def commHelp(message,client,sClass,**kwargs):
    strings = message.content.split(None,1)
    helptext=stringOps(data=defaultHelpText,sClass=sClass)
    msg=""
    if len(strings)<2:
        msg=helptext
    else:
        searchText=strings[1].strip()
        for comm,usage in usages.items():
            if searchText in comm or searchText in usage:
                msg+='*'+comm.replace(searchText,'__'+searchText+'__')+'* '+usage.replace(searchText,'__'+searchText+'__')+'\n'
        if not msg:
            msg='No results in helptext containing "'+searchText+'"'
    await client.send_message(message.channel,msg)
commDispatcher['help']=partial(commHelp)
usages['help']='**<search text>**Displays the helptext. Optionally, search helptext for keyword'
#==================================#
async def commRandom(message,client,**kwargs):
    formats=['I choose number **{0}**!','**{0}** seems good.','Hmmm... What about **{0}**?','RANDOM_NUMBER_CHOSEN: #**{0}** (beep boop)']
    strings = message.content.split()
    if len(strings) < 3 or not isInt(strings[1]) or not isInt(strings[2]):
        raise CommUsage(strings[0])
    randNum=random.randint(int(strings[1]),int(strings[2]))
    msg=random.choice(formats).format(str(randNum))
    await client.send_message(message.channel,msg)
commDispatcher['random']=partial(commRandom)
usages['random']='**<high> <low>** Generate a random number between high and low'
#==================================#
async def commChoose(message,client,**kwargs):
    formats=['I pick "{0}"!','"{0}" seems good.','Hmmm... What about "{0}"?','RANDOM_OPTION_CHOSEN: "{0}" (beep boop)']
    strings =message.content.split(None,1)
    if len(strings) < 2:
        raise CommUsage(strings[0])
    options = strings[1].split('|')
    if len(options) < 1:
        raise CommUsage(strings[0])
    choice=random.choice(options)
    msg=random.choice(formats).format(choice)
    await client.send_message(message.channel,msg)
commDispatcher['choose']=partial(commChoose)
usages['choose']='**<choice1|choice2|choice3|...>** Chooses randomly from the given options'
#==================================#
async def commServerStats(message,client,server,**kwargs):
    msg = '**Stats for ' + server.name + ':**\n'
    numUsers = 0
    numBots = 0
    for member in server.members:
        if member.bot: numBots+=1
        else: numUsers+=1
    totalUsers = numUsers + numBots
    msg+='*Total Users:* ' + str(totalUsers) + '\n*Humans:* ' + str(numUsers) + '\n*Bots:* ' + str(numBots)
    await client.send_message(message.channel,msg)
commDispatcher['serverstats']=partial(commServerStats)
usages['serverstats']='Get some stats on this server'
#==================================#
async def commRemind(message,client,**kwargs):
    strings=message.content.split()
    if len(strings) < 3 or not isInt(strings[1]):
        raise CommUsage(strings[0])
    remindTime=timeToSec(strings[1])
    msg = ' '.join(strings[2::])
    rmd=Reminder(client,message,msg,remindTime)
    await rmd.run()
commDispatcher['remindme']=partial(commRemind)
usages['remindme']='**<time h\:m\:s> <message>** Send a reminder after the given time'
#==================================#
async def commWiki(message,client,**kwargs):
    #Split up Strings
    strings = message.content.split()
    if len(strings) < 2:
        raise CommUsage(strings[0])
        return
    del strings[0]
    query = ' '.join(strings)
    print('Wiki query: ' + query)
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
    messageText=truncate(messageText,1000,'...`')
    await client.send_message(message.channel, messageText)
commDispatcher['wiki']=partial(commWiki)
usages['wiki']='**<thing>** Search something up on wikipedia'
#==================================#
async def commInvite(message,client,server,**kwargs):
    #Check to see if bot has already made an invite
    serverInvites=await client.invites_from(server)
    myInvite=None
    for inv in serverInvites:
        if inv.inviter==client.user and inv.max_age==0 and not inv.revoked:
            myInvite=inv
            break
    if myInvite is None:
        myInvite=await client.create_invite(destination=message.channel,max_age=0,max_uses=0,temporary=False,unique=True)
    await client.send_message(message.channel,'Invite: ' + myInvite.url)
commDispatcher['invite']=partial(commInvite)
usages['invite']='Get an invite to this server'
#==================================#
#ADMIN COMMANDS====================#
async def commPurge(message,client,**kwargs):
    strings=message.content.split()
    if not hasPerm(message.author,'manage_messages',message.channel):
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
commDispatcher['purge']=partial(commPurge)
usages['purge']='Purge (delete) the number of messages specified in the current channel {Requires "manage_messages"}'
#==================================#
async def commCommPrefix(message,client,sClass,**kwargs):
    strings=message.content.split()
    if not hasPerm(message.author,'manage_server',message.channel):
        raise NoPerm(strings[0])
    if len(strings) < 2:
        raise CommUsage(strings[0])
    oldcommandPrefix = sClass.commandPrefix
    sClass.commandPrefix = strings[1].strip()
    await client.send_message(message.channel, 
    'The command prefix for this server was changed from \"' + oldcommandPrefix + '\" to \"' + sClass.commandPrefix + '\".')
commDispatcher['commandprefix']=partial(commCommPrefix)
usages['commandprefix']='**<character>** Change this server\'s command prefix {Requires "manage_server"}'
#==================================#
async def commCustomCommand(message,client,sClass,**kwargs):
    strings=message.content.split()
    if not hasPerm(message.author,'manage_server',message.channel) and (strings[1]=='create' or strings[1]=='delete'):
        raise NoPerm(strings[0]+' '+strings[1])
    if len(strings)<2:
        raise CommUsage(strings[0])
    #Parse first argument
    if strings[1]=='help':
        await customCommHelp(message,client,sClass)
    elif strings[1]=='create':
        await customCommCreate(message,client,sClass)
    elif strings[1]=='delete':
        await customCommDelete(message,client,sClass)
    elif strings[1]=='list':
        await customCommList(message,client,sClass)
commDispatcher['customcommand']=partial(commCustomCommand)
usages['customcommand']='**<help|list|create|delete>** Manage this server\'s custom commands. See customcommand help for more info {Requires "manage_server" for creation/deletion}'
#==================================#


def commUsages(command:str,commandPrefix:str=defaultCommandPrefix):
    usage='`'+commandPrefix+command+'` '+usages[command] if command in usages else 'No information on command `'+commandPrefix+command+'` found.'
    return usage
    
def stringOps(data:str,sClass:serverClass=None,server:discord.server=None):
    #Generic replacements
    data = data.replace('$date$',datetime.now().strftime("%m/%d/%Y"))
    #Server Specific replacements
    if sClass is not None:
        data=data.replace('$commands$','\n'.join([commUsages(comm,sClass.commandPrefix) for comm in usages.keys()]))
    if server is not None:
        data = data.replace('$serverName$',client.get_server(sClass.id).name)
    return data

def hasPerm(member,permission,channel):
    userPerms= dict(channel.permissions_for(member))
    return userPerms[permission]