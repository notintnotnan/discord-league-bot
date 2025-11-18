from enum import Enum

class Commands(str, Enum):
    
    def __new__(cls, command, description, instructions):
        obj = str.__new__(cls, command)
        obj._value_ = command
        obj.description = description
        obj.instructions = instructions
        return obj
    
    LISTCOMMANDS = ("listCommands","Shows the list of the available commands and their description","!listCommands")
    SHOW = ('show','Shows the description and the instructions for the referenced command.', '!show <command>')
    JOINPARTY = ("joinParty","Adds the summoner data to the database.", "!joinParty <summonerName>#<tagLine>")
    SHOWPLAYER = ("showPlayer", "Shows the queue data of the specified player.","!showPlayer <summonerName>#<tagLine>")
    DELETELAYER = ("deletePlayer", "Deletes the player from the database.","!deletePlayer <summonerName>#<tagLine>")
    NOTFOUND = ("","It doesn't exist.","Not much to show about that.")

def command_info(command):
    try:
        return list(filter(lambda x : x.value == command, Commands))[0]
    except:
        return Commands.NOTFOUND