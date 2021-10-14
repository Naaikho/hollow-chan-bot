# -*- coding: utf-8 -*-

import discord
import traceback
import asyncio
import time
import os, sys
import json
import random
from discord.ext import commands
from typing import Union
from lib.ndiscord import exst, path, pathGuild, saveGuildData, pathAcc, saveUsersData, loadGuildData
from lib.userProfile import userAccount

# WD: Working Directory
WD = sys.path[0]

# get thhe cards status in database
def cardLoader() -> dict:
    """ Return a `dict` with all cards stats """
    global WD
    
    return json.loads(exst(path(WD, "src", "cards_links.json")))

# select randomly a card with rarity
def cardSelector(channels: list) -> dict:
    """ Select a radom card from the ``cards_link.json`` and a random channel from the list of authorized channel """

    cards = cardLoader()
    c = random.randrange(1, 105)
    channel = random.choice(channels)
    lvl = 0
    if c in range(1, 51):
        lvl = 1
    if c in range(51, 77):
        lvl = 2
    if c in range(77, 93):
        lvl = 3
    if c in range(93, 104):
        lvl = 4
    if c == 104:
        lvl = 5
    print("n{}".format(lvl))
    for nx in ["n4", "n5"]:
        for crd in cards[nx].copy().values():
            if crd["claimed"]:
                del cards[nx][crd["id"]]
    if list(cards["n{}".format(lvl)].keys()) == []:
        return cardSelector(channels)
    card = random.choice(list(cards["n{}".format(lvl)].keys()))
    card = cards["n{}".format(lvl)][card]

    return {"url":card["url"], "id":card["id"], "anime":card["anime"], "name":card["name"], "lvl":lvl}, channel

def get_card(id:str, account="") -> Union[dict, None]:
    """ Return the stats of a card in the user cards inventory """

    if isinstance(account, userAccount):
        cards = account.cards
    elif account == "":
        cards = cardLoader()
    else:
        return None
    for nx in cards.items():
        if id in nx[1].keys():
            return nx[1][id]
    return None

# return the selected card in database
def getShopCard(card_id: str, guild: int) -> Union[None, dict]:
    guild = loadGuildData(guild)
    for card in guild["shop"]["cards"]:
        if card != {}:
            if card_id == card["id"]:
                return card
    return None

def swapCards(user_recv: userAccount, user_give: userAccount, card: dict):
    """ exchange the ``card`` from ``user_give`` to ``user_recv`` """
    if card["id"] in user_recv.cards["n{}".format(card["lvl"])].keys():
        user_recv.cards["n{}".format(card["lvl"])][card["id"]]["nb"] += 1
        card["nb"] -= 1
        if card["nb"] == 0:
            del user_give.cards["n{}".format(card["lvl"])][card["id"]]
    else:
        user_recv.cards["n{}".format(card["lvl"])][card["id"]] = card.copy()
        user_recv.cards["n{}".format(card["lvl"])][card["id"]]["nb"] = 1
        if card["lvl"] in range(4, 6):
            cards = cardLoader()
            cards["n{}".format(card["lvl"])][card["id"]]["user"] = user_recv.id
            with open(path(WD, "src", "cards_links.json"), "w") as data:
                json.dump(cards, data, indent=4)
        card["nb"] -= 1
        if card["nb"] == 0:
            del user_give.cards["n{}".format(card["lvl"])][card["id"]]
    user_give.save()
    user_recv.save()

async def showShop(ctx: commands.Context, emojis: dict):
    """ Send an embed with the shop guild contents in the channel """
    shop: dict = loadGuildData(ctx.guild.id)["shop"]
    emb = discord.Embed(title="🛍   __SHOP__   🛍", description="\u200B", colour=0xb45ddf)
    emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    if shop["update"] == "":
        shop["update"] = "Empty shop"
    else:
        shop["update"] = "Update: " + shop["update"]
    emb.set_thumbnail(url="...")
    emb.set_footer(text=shop["update"], icon_url="...")
    i = 0
    l = 0
    for card in shop["cards"]:
        if l == 2:
            emb.add_field(name="\u200B", value="\u200B", inline=True)
            l = 0
        if card != {}:
            emb.add_field(name="Card: `{}`".format(i+1),
            value="{emoji} • **[{name}]({url})**\n• Level: `{lvl}`\n• Anime: `{anime}`\n• Id: `{id}`\n• Price: `{price}`".format(emoji=emojis["card"],
            name=card["name"],
            url=card["url"],
            anime=card["anime"],
            id=card["id"],
            lvl=(emojis["star"] * card["lvl"]),
            price=card["price"]),
            inline=True)
        else:
            emb.add_field(name="Card: `{}`".format(i+1), value="• *This location is empty.*")
        i += 1
        l += 1
    emb.add_field(name="\u200B", value="\u200B", inline=True)
    return await ctx.send(embed=emb)

async def showShopItem(ctx: commands.Context, emojis: dict, card: dict):
    """ Send an embed that contains more information about the ``card_id`` """
    emb = discord.Embed(title=emojis["card"] + " • {}".format(card["name"]), description="\n• **Level:** `{lvl}`\n• **Anime:** `{anime}`\n• **Id:** `{id}`\n• **Price:** `{price}`".format(
        lvl=(emojis["star"] * card["lvl"]),
        anime=card["anime"],
        id=card["id"],
        price=card["price"]))
    emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    emb.set_thumbnail(url="...")
    emb.set_image(url=card["url"])
    return await ctx.send(embed=emb)

async def buyShopItem(ctx: commands.Context, emojis: dict, card: dict):
    """ Allows users to purchase a card for sale in the shop """
    user = userAccount(ctx.author)

    if card["id"] in user.cards["n{}".format(card["lvl"])].keys():
        user.cards["n{}".format(card["lvl"])][card["id"]]["nb"] += 1
    else:
        user.cards["n{}".format(card["lvl"])] = {card["id"]:get_card(card["id"])}
        user.cards["n{}".format(card["lvl"])][card["id"]]["nb"] = 1
    user.money -= card["price"]
    user.save()

# remove the selected card in the shop
async def removeShopCard(ctx: commands.Context, card: dict):
    guild = loadGuildData(ctx.guild.id)
    guild["shop"]["cards"][card["index"]] = {}
    saveGuildData(guild)

async def setShop(ctx: commands.Context, card: dict, price: int, index: int):
    """ Allows admins to set the shop """
    import datetime

    guild = loadGuildData(ctx.guild.id)
    card["index"] = index
    card["price"] = price
    if "claimed" in card:
        del card["claimed"]
        del card["user"]
    guild["shop"]["cards"][index] = card.copy()
    date = datetime.datetime.now()
    guild["shop"]["update"] = "{}/{}/{} at {}:{}".format(date.day, date.month, date.year, date.hour if date.hour >= 10 else "0" + str(date.hour), date.minute if date.minute >= 10 else "0" + str(date.minute))
    saveGuildData(guild)