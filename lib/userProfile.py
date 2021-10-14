# -*- coding: utf-8 -*-

import sys, os, json
from typing import Union
import discord
from discord.ext import commands
from lib.ndiscord import exst, path, pathAcc, saveUsersData, loadUsersData

# WD: Working Directory
WD = sys.path[0]

# manage users account
class userAccount():
    """
    User:
    -----
    `id`
    `str_id`
    `name`
    `tag`
    `botStatus`
    `money`
    `cards`
    `avatar_url`
    `mention`
    `is_exchange`
    
    Methods:
    --------
    `export`: return a dict with the account\n
    `save`: save all infos in the user `json` """
    
    def __init__(self, user: discord.Member):
        userExist = True

        self.usersData = loadUsersData(user.id)
        if self.usersData is None:
            self.usersData = json.loads(exst(path(WD, "src", "templates", "user_template.json")))
            userExist = False

        self.id = user.id
        self.str_id = str(self.id)
        self.name = user.name
        self.tag = user.discriminator
        self.botStatus = user.bot
        self.money = self.usersData["inventory"]["money"]
        self.cards = self.usersData["inventory"]["cards"]
        self.avatar_url = user.avatar_url
        self.mention = user.mention
        self.is_exchange = self.usersData["is_exchange"]

        if not userExist:
            self.save()
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.id == other.id

    def export(self) -> dict:
        return {"id":self.id, "name":self.name, "tag":self.tag, "mention":self.mention,"botStatus":self.botStatus, "is_exchange":self.is_exchange, "inventory":{"money":self.money, "cards":self.cards}}
    
    def save(self):
        self.usersData = self.export()
        saveUsersData(self.usersData)