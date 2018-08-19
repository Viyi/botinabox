import discord
import asyncio

async def customCommHelp(message,client,sClass):
    commPref=sClass.commandPrefix
    text="***BotInABox Custom Commands Helpfile, v0.0.1***\n**<=======================================================>**\n"
    text+='**Commands:**\n'
    text+='`'+commPref+'customcommand help` See this helpfile\n'
    text+='`'+commPref+'customcommand list` List available custom commands\n'
    text+='`'+commPref+'customcommand create` **<command_name> <response>** Creates a custom command.\n'
    text+='`'+commPref+'customcommand delete` **<command_name>** Deletes a custom command.\n'
    text+='**Formatting/Variables:**\n'
    text+='`{userM}` A mention for the user running the command\n'
    text+='`{userN}` The name of the user running the command\n'
    text+='`{0} {1} {2} ...` Individual arguments supplied by the user, in order\n'
    text+='`{args}` *All* arguments supplied by the user, including spaces\n'
    text+="**<=======================================================>**"
    await client.send_message(message.channel,text)

async def customCommCreate(message,client,sClass):
    usage='`'+sClass.commandPrefix+'customcommand create` **<command_name> <response>** Creates a custom command.\nThe following variables are available to use:\n'
    usage+='`{userM}` A mention for the user running the command\n'
    usage+='`{userN}` The name of the user running the command\n'
    usage+='`{0} {1} {2} ...` Individual arguments supplied by the user, in order\n'
    usage+='`{args}` *All* arguments supplied by the user, including spaces'
    strings=message.content.split()
    if len(strings)<4:
        await client.send_message(message.channel,usage)
        return
    commName=strings[2]
    if commName[0]==sClass.commandPrefix: commName=commName[1:]
    if commName =='help' or commName=='customcommand':
        await client.send_message(message.channel,'*Sorry, you cannot overwrite the built-in `'+sClass.commandPrefix+commName+'` command.*')
        return
    response=message.content.split(None,3)[3]
    overwrite=commName in sClass.customCommands
    sClass.customCommands[commName]=response
    await client.send_message(message.channel,'*'+('Overwrote' if overwrite else 'Created')+ '  command `'+sClass.commandPrefix+commName+'`.*')

async def customCommRun(message,client,sClass):
    strings=message.content.split()
    command = strings[0][1:]
    userArgs=strings[1:]
    allUserArgs=(message.content.split(None,1)[1] if len(message.content.split(None,1))>1 else "")
    response=customCommOps(sClass.customCommands[command],userArgs,allUserArgs,message,client,sClass)
    await client.send_message(message.channel,response)

async def customCommDelete(message,client,sClass):
    usage='`'+sClass.commandPrefix+'customcommand delete` **<command_name> Deletes a custom command.'
    strings=message.content.split()
    if len(strings)<3:
        await client.send_message(message.channel,usage)
        return
    commName=strings[2]
    if commName[0]==sClass.commandPrefix: commName=commName[1:]
    if commName not in sClass.customCommands.keys():
        await client.send_message(message.channel,'*Custom command `'+sClass.commandPrefix+commName+'` not found.*')
        return
    sClass.customCommands.pop(commName,None)
    await client.send_message(message.channel,'*Custom command `'+sClass.commandPrefix+commName+'` deleted.*')

async def customCommList(message,client,sClass):
    msg='***Custom Commands:***\n'
    msg+=('\n'.join(['`'+sClass.commandPrefix+comm+'` '+resp for comm,resp in sClass.customCommands.items()]))
    await client.send_message(message.channel,msg)

def customCommOps(text,userArgs,allUserArgs,origMessage,client,sClass):
    #User mentions
    text=text.replace('{userM}',origMessage.author.mention)
    #User name
    text=text.replace('{userN}',origMessage.author.name)
    #All user args
    if allUserArgs: text=text.replace('{args}',allUserArgs)
    #Numbered user args
    n=0
    for arg in userArgs:
        text=text.replace('{'+str(n)+'}',arg)
        n+=1
    return text