import discord #For discord functionality
import asyncio #For Async operations (needed by Discord)
from datetime import datetime#For date/time functions... who'd have guessed
import sys,os
sys.path.insert(0,'.')
#My files
from src.utils.utils import *
from src.utils.bGlobals import *
from src.commands.commands import *
from src.commands.customcommand import *
#GLOBALS===========================#
clientID='id_here'
client = discord.Client()
sClasses={}
#==================================#

#DISCORD CODE======================#
#When the bot is ready
@client.event
async def on_ready():
    #Header Info
    print('Succesfully logged in:')
    print('Name: '+client.user.name)
    print('ID: '+client.user.id)
    status = 'Mention me for help!'
    await client.change_presence(game=discord.Game(name=status,url='https://github.com/wolfinabox/botinabox'))
    print('Status set to: \"' + status + '\"')
    if discord.opus.is_loaded(): print('Opus Codecs Loaded Successfully!')
    else: pLog('WARN: Opus Codecs Not Loaded!')
    #JSON Path
    if not os.path.exists(os.path.join(script_dir,'resources','servers')): os.makedirs(os.path.join(script_dir,'resources','servers'))
    #Set up new servers
    print('Servers:')
    for server in client.servers:
        temp=loadServer(server.id)
        if temp:
            sClasses[server.id]=temp
            print('  Loaded: "'+server.name+'", '+server.id)
        else:
            sClasses[server.id]=serverClass(server.id) #Make association
            print('  Created: "'+server.name+'", '+server.id)
            
    #    for channel in server.channels: 
    #        if channel.name.lower()==sClasses[server.id].logChannelName:
    #            sClasses[server.id].logChannel=channel
        print('  Members: '+str(sum(1 for x in server.members)))
    #    print('  Log Channel:'+('"'+sClasses[server.id].logChannel.name+'"' if sClasses[server.id].logChannel is not None else 'None'))
        saveServer(sClasses[server.id])
        print('------')
    
    elapsedTime = datetime.now() - startTime
    pLog('Bot started successfully! Took ' + str(elapsedTime.seconds) + '.' + truncate(str(elapsedTime.microseconds),2) + ' seconds')
    print('------------------')

#When we get a message
@client.event
async def on_message(message):
    beginTime = datetime.now()

    #If the message belongs to the bot, ignore it
    if message.author == client.user:
        return
    #We can't handle PM's just yet, so any message with no server should be
    #ignored.
    if message.server == None:
        return

    sClass=sClasses[message.server.id]

    if message.content.strip().startswith(sClass.commandPrefix):
        await client.send_typing(message.channel)
        strings=message.content.strip().split()
        command=strings[0][1:].lower()
        #It's a custom command
        if command in sClass.customCommands.keys():
            await customCommRun(message,client,sClass)
        #It's a regular command
        elif command in commandDict.keys():
            try:
                await commandDict[command]['function'](message=message,client=client,sClass=sClass,server=message.server)
            except CommUsage as e:
                await client.send_message(message.channel,commUsages(command))
            except NoPerm as e:
                await client.send_message(message.channel,'You do not have permission to use "'+sClass.commandPrefix+command+'"')
        #It's not recognised
        else:
            msg=""
            strings=message.content.split()
            allCommands={**commandDict,**sClass.customCommands}
            percentages={}
            for comm in allCommands.keys():
                percentages[comm]=round(similar(strings[0],comm) * 100,1)
            mostLikelyPercent = max(v for k, v in percentages.items())
            msg+="*Sorry, I don't recognise \"" + strings[0] + "\"*\n"
            if (mostLikelyPercent > 40):
                msg+="*Did you mean:*\n"
                for key,value in sorted(percentages.items(), key=lambda x:x[1],reverse=True):
                   if (value > 40):
                         msg+="*(" + str(value) + "%)* `" + key + "`\n"
            else:
                msg+="*Try " + sClass.commandPrefix + "help to see all commands.*"
            await client.send_message(message.channel, msg)
   


    elif client.user.mentioned_in(message) and len(message.content.split())<2:
        await commandDict['help']['function'](message=message,client=client,sClass=sClass,server=message.server)


#Start bot
startTime = datetime.now()
try:
    clientID=loadID()
    client.run(clientID)
except discord.LoginFailure as e:
    pLog('The clientID in "token.txt" appears to be incorrect. Please double-check that you used the correct\n bot id from https://discordapp.com/developers/applications/me.')
    pLog(str(e))
    client.close()
    #input()
except FileNotFoundError as e:
    pLog('Please create a file named "token.txt" next to this executable, and place the token of your bot,\nfrom https://discordapp.com/developers/applications/me, inside it.')
    pLog(str(e))    
    client.close()
    #input()
except Exception as e:
    pLog('I can\'t connect to the Discord servers right now, sorry! :(\nCheck your internet connection, and then https://twitter.com/discordapp for Discord downtimes,\n and then try again later.')
    pLog(str(e))
    client.close()
    #input()

#END DISCORD CODE