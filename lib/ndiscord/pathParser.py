# -*- coding: utf-8 -*-

import os, sys
from typing import Union
import discord

# WD: Working Directory
WD = sys.path[0]

def path(*args) -> str:
    """ Minimize ``os.path.join()`` """
    path = args[0]
    for arg in args:
        path = os.path.join(path, arg)
    return path

def pathGuild(guild: Union[str, int]) -> str:
    """ Return the path to ``./src/data/guildsData.json`` """
    global WD

    return path(WD, "src", "data", "guilds", "{}.json".format(guild))

def pathAcc(user: Union[str, int]) -> str:
    """ Return the path of ``userAccount`` json file """
    global WD

    return path(WD, "src", "data", "users", "{}.json".format(user))