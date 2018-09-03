import os
import json
from datetime import datetime
from difflib import SequenceMatcher 
from utils.bGlobals import *
from storageclasses.serverclass import *
#GLOBALS===========================#
max_logs=150
#==================================#

def loadID(location:str=os.path.join(script_dir, 'token.txt')):
    """
    Loads the bot's client ID from the "token.txt" file
    :returns: The loaded ID
    :throws: FileNotFoundError, if token.txt file not found
    """
    file = open(location)
    id=file.readline().strip()
    return id

def pLog(message:str,logFilePath:str=os.path.join(script_dir, 'log.txt')):
    """
    Prints and logs the given message to file
    :param message: The message to print/log
    :param logFilePath: The path to the logging file
    """
    print(message)
    log(message,logFilePath)

def log(message:str,logFilePath:str=os.path.join(script_dir, 'log.txt')):
    """
    Logs the given message to file
    :param message: The message to log
    :param logFilePath: The path to the logging file
    """
    message=message.replace('\n',' ').replace('\r',' ')
    try:
        num_lines = sum(1 for line in open(logFilePath))
        if num_lines>=max_logs:
            lines=open(logFilePath, 'r').readlines()
            del lines[0]
            lines.append(datetime.now().strftime('[%m/%d/%Y-%H:%M:%S]: ')+message+'\n')
            with open(logFilePath,'w') as file:
                file.writelines(lines)
        else:
            with open(logFilePath,'a') as file:
                file.write(datetime.now().strftime('[%m/%d/%Y-%H:%M:%S]: ')+message+'\n')
    except IOError:
        with open(logFilePath,'w') as file:
            file.write(datetime.now().strftime('[%m/%d/%Y-%H:%M:%S]: ')+message+'\n')

def truncate(data:str,length:int,append:str=''):
    """
    Truncates a string to the given length
    :param data: The string to truncate
    :param length: The length to truncate to
    :param append: Text to append to the end of truncated string
    """
    return (data[:length]+append) if len(data)>length else data

def isInt(s:str):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def timeToSec(s:str):
    #Format: 00:00:00 (hour:minute:second)
    seconds=0
    strings=s.split(':')
    if len(strings)>3: raise ValueError()
    multiplier=1
    for string in strings[::-1]:
        if not isInt(string): raise ValueError()
        seconds+=(int(string)*multiplier)
        multiplier*=60
    return seconds

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def any_in(a, b):
  return not set(a).isdisjoint(b)

def loadServer(id,folderPath=os.path.join(script_dir,'resources','servers')):
    path=os.path.join(folderPath,id+'.json')
    #If the file does not exist
    if not os.path.isfile(path): return None
    temp={}
    with open(path,'r') as f:
        temp=json.load(f)
    sClass=serverClass(temp['id'])
    if 'commandPrefix' in temp: sClass.commandPrefix=temp['commandPrefix']
    if 'customCommands' in temp: sClass.customCommands=temp['customCommands']
    return sClass

def saveServer(serverClass,folderPath=os.path.join(script_dir,'resources','servers')):
    path=os.path.join(folderPath,serverClass.id+'.json')
    data={'id':serverClass.id,'commandPrefix':serverClass.commandPrefix,'customCommands':serverClass.customCommands}
    with open(path,'w') as f:
        json.dump(data,f,indent=4)
    

class CommUsage(Exception):
    def __init__(self,arg):
        self.sterror = arg
        self.args = {arg}

class NoPerm(Exception):
    def __init__(self,arg):
        self.sterror = arg
        self.args = {arg}