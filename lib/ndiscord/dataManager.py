# -*- coding: utf-8 -*-

import sys, os, json
from typing import Union
import discord
from discord.ext import commands
from .pathParser import path, pathGuild, pathAcc

WD = sys.path[0]

def exst(file) -> Union[str, None]:
    """ Check if the path of ``file`` exist and open it. """
    if os.path.exists(file):
        with open(file, "r") as data:
            return data.read()
    else:
        return None

def saveGuildData(data:dict) -> None:
    """ Save the data of a guild in a ``.json`` with the ``id`` of the guild in name """
    with open(pathGuild(data["id"]), "w") as f:
        json.dump(data, f, indent=4)

def saveUsersData(data:dict) -> None:
    """ Save the data of a user in a ``.json`` with the ``id`` of the user in name """
    with open(pathAcc(data["id"]), "w") as f:
        json.dump(data, f, indent=4)

def loadGuildData(guild: Union[str, int]) -> dict:
    """ Load the `guild` data """
    if os.path.exists(pathGuild(guild)):
        with open(pathGuild(guild), "r") as f:
            return json.load(f)
    else:
        return None

def loadUsersData(user: Union[str, int]) -> dict:
    """ Load the `user` data """
    if os.path.exists(pathAcc(user)):
        with open(pathAcc(user), "r") as f:
            return json.load(f)
    else:
        return None

# return all guilds saved in database
def loadCompletGuilds() -> dict:
    jsonPath = path(WD, "src", "data")
    guildData = {}
    for file in os.listdir(path(jsonPath, "guilds")):
        if ".json" in file:
            guild = file.split(".")[0]
            guildData[guild] = loadGuildData(guild)
    return guildData