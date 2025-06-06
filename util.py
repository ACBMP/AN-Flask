import datetime
import discord
import random

def connect():
    """
    very basic connect to port 27017 mongodb client
    """
    from flask_pymongo import PyMongo
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017')
    db = client.public
    return db


def identify_player(db, name):
    """
    identify a player by trying the name first then igns
    case insensitive
    """
    import re
    rename = re.compile(name, re.IGNORECASE)
    player = db.players.find_one({"name" : rename})
    if player is None:
        player = db.players.find_one({"ign": rename})
    if player is None:
        player = db.players.find_one({"discord_id": name.replace("@!", "").replace(">", "").replace("<", "")})
    if player is None:
        raise ValueError(f"identify_player: player {name} not found")
    return player


# mode checker
def check_mode(mode, server=None, short=False):
    # default modes for servers
    if server and not mode:
        if server in conf.e_servers:
            return "e" if short else "escort"
        elif server in conf.mh_servers:
            return "mh" if short else "manhunt"
        elif server in conf.dm_servers:
            return "dm" if short else "deathmatch"
        elif server in conf.aa_servers:
            return "aa" if short else "artifact assault"
        else:
            return "manhunt"
    mode = mode.lower()
    # if server wasn't specified use abbreviations
    if mode in ["m", "mh", "manhunt"]:
        return "mh" if short else "manhunt"
    elif mode in ["e", "escort"]:
        return "e" if short else "escort"
    elif mode in ["au", "among", "among us"]:
        return "au" if short else "among us"
    elif mode in ["dm", "deathmatch", "dmatch"]:
        return "dm" if short else "deathmatch"
    elif mode in ["aa", "artifact assault"]:
        return "aa" if short else "artifact assault"
    elif mode in ["aar", "artifact assault running"]:
        return "aar" if short else "artifact assault running"
    elif mode in ["aad", "artifact assault defending"]:
        return "aad" if short else "artifact assault defending"
    else:
        raise ValueError("check_mode: Unsupported mode found.")


def att_to_file(message, n=0):
    # I was having issues getting this working without saving separately
    import requests
    _att = requests.get(message.attachments[n].url)
    fname = f"sync/{message.attachments[n].filename}"
    with open(fname, "wb") as f:
        f.write(_att.content)
    with open(fname, "rb") as f:
        att = discord.File(f, filename="image.png")
    return att


# some fun ACB insults to use as error messages
insults = ["You suck.", "ur mam gay", "Even fouadix speaks English better than you.",
        "I bet you'd choose sex over escort.", "Go back to wanted.", "You played on Xbox, didn't you?",
        "I'd choose Fazz over you.", "Even Fazz kills less civis than you.", "Dell runs less than you.",
        "Are you from AC4?", "Speed gets fewer deaths than you.", "tdas gay", "ultro is trans", "What the fuck is that?",
        "Let's not do that again.", "I just want to punch myself in the fucking face.", "Really fucking hilarious.",
        "Dude, I'ma slaughter your entire family if you ever do that again.", "Oh man, I hate you.", "u r getting scummy",
        "If only you could fuck up the escort never.", "Welcome to TCG.", "You turbotrolled more than Omse.",
        "Do your fucking job I can't do mine.", "You go in, I'm not even there, and then you wonder waroi waroi."]

def find_insult():
    return random.choice(insults)


def command_dec(func):
    """
    command decorator with proper error handling
    this doesn't seem to work yet and I genuinely have NO idea how to get it working lol
    """
    async def exceptionhandler(*arg):
        try:
            await func(*arg)
        except Exception as e:
            print(e)
            client = discord.Client()
            await client.fetch_channel(arg[2].id).send(str(e) + " " + find_insult())
    return exceptionhandler


