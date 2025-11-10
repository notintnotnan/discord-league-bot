from enum import Enum

class Commands(str, Enum):
    
    def __new__(cls, command, description, instructions):
        obj = str.__new__(cls, command)
        obj._value_ = command
        obj.description = description
        obj.instructions = instructions
        return obj
    
    JOINPARTY = ("joinParty","Adds the summoner data to the database.", "!joinParty <summonerName>#<tagLine>")
    NOTFOUND = ("","It doesn't exist.","Not much to show about that.")

def command_info(command):
    try:
        return list(filter(lambda x : x.value == command, Commands))[0]
    except:
        return Commands.NOTFOUND