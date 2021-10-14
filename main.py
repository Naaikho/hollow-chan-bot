# -*- coding: utf-8 -*-

try:
    import traceback
    from asyncio import sleep
    import os, sys, platform
    import json
    import string
    import random
    import datetime
    import requests
    from typing import Union
    import discord
    from discord.ext import commands
    from captcha.image import ImageCaptcha
    from lib.ndiscord import exst, path, pathGuild, saveGuildData, pathAcc, loadGuildData, loadCompletGuilds
    from lib.userProfile import userAccount
    from lib.cardManager import cardLoader, cardSelector, get_card, swapCards, showShop, showShopItem, buyShopItem, setShop, getShopCard, removeShopCard
except Exception as e:
    print(e)
    # install python libs with pip if they're not installed
    from subprocess import Popen, PIPE
    if platform.system() == "Windows":
        installer = "py -m pip install discord.py captcha"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        installer = "pip3 install discord.py captcha"
    else:
        print("That script require:\n - discord.py\n - captcha\n\npip install <requirements>")
        exit()
    print("Install requirements . . .")
    require = Popen(installer, shell=True, stdout=PIPE, stderr=PIPE)
    succes, err = require.communicate()
    if succes != b"":
        print(succes.decode())
    if err != b"":
        print("Can't install dependencies...\n")
        print(err.decode())
        input("Press enter . . .")
        exit()
    print("Restart the script for apply modifications.")
    input("Press enter . . .")
    exit()

# ------------------------------ # Glogals Variables # ------------------------------ #

# WD: Working Directory
WD = sys.path[0]
PREFIX = "$"
BOT_NAME = "AnimeBot"
# Save captcha datas
captchaData = {}
# temp value during exchange
exchange = {}
# emotes list
emojis = {"card":"🎴", "star":"⭐", "nostar":"◾", "money":"💎", "admin":"⚙️", "user":"💠"}
# stock page of an Embed when his called
pages = {}
# contain time of appearance of certain messages in milliseconds
delete_after = {}
delete_after["drop"] = 1800.0
delete_after["error"] = 15.0
delete_after["validating"] = 8.0

# ----------------------------------------------------------------------------------- #

# get bot token in "token.json"
tokend = json.loads(open(os.path.join(sys.path[0], "src", "token.json"), "r").read())

# check args on launch for Linux& Mac
if platform.system() == "Linux" or platform.system() == "Darwin":
    try:
        if sys.argv[1].upper() == "DEBUG":
            mode = "DEBUG"
        else:
            mode = "DEFAULT"
    except IndexError:
        mode = "DEFAULT"

# check args on launch for Windows
if platform.system() == "Windows":
    with open(os.path.join(sys.path[0], "src", "args.json"), "r") as data:
        args = json.loads(data.read())["args"]
        if args.upper() == "DEBUG":
            mode = args
        else:
            mode = "DEFAULT"

if mode.lower() == "debug":
    token = tokend["testbot"]
    if token == "":
        print("Debug mode can't be loaded. 'testbot' token in 'token.json' is empty.")
        mode = "default"
if mode.lower() == "default":
    token = tokend[BOT_NAME]

# see if the necessary files and folders exist
if not os.path.exists(path(WD, "src", "data")):
    # and create them otherwise
    os.mkdir(path(WD, "src", "data"))
if not os.path.exists(path(WD, "src", "data", "guilds")):
    os.mkdir(path(WD, "src", "data", "guilds"))
if not os.path.exists(path(WD, "src", "data", "users")):
    os.mkdir(path(WD, "src", "data", "users"))

# check if the prefix is edited
if not os.path.exists(path(WD, "src", "prefix")):
    with open(path(WD, "src", "prefix"), "w") as data:
        data.write(PREFIX)
else:
    with open(path(WD, "src", "prefix"), "r") as data:
        PREFIX = data.read()

# return the set mode (debug (test token) or default (default token))
print("Mode: {}".format(mode.capitalize()))

# allows the bot to see other members of a server
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# clear the captchas images file
delPath = os.path.join(WD, "src", "data")
for img in os.listdir(delPath):
    if ".png" in img:
        os.remove(path(delPath, img))
del delPath


# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #



# return error with traceback
def print_traceback(error):
    global WD

    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    if not os.path.exists(path(WD, "src", "crash")):
        os.mkdir(path(WD, "src", "crash"))
    date = datetime.datetime.now()
    with open(path(WD, "src", "crash", str(type(error)) + "-" + "{}:{}_{}-{}-{}".format(date.hour if date.hour >= 10 else "0" + str(date.hour),
    date.minute if date.minute >= 10 else "0" + str(date.minute),
    date.day,
    date.month,
    date.year)),
    "w") as data:
        data.write("\n".join(traceback.format_exception(type(error), error, error.__traceback__)))

# remove the not allowed characters
def sepChar(s:str, chars:str, join:str) -> str:
    for c in chars:
        s = join.join(s.split(c))
    return s

# remove the choice listener after "sec"
async def tmpChoice(guildId: str, sec: int):
    await sleep(sec)
    try:
        guildData = loadGuildData(guildId)
        del guildData["reac_id"]
        saveGuildData(guildData)
    except Exception:
        return

# delete message after "sec"
async def tmpDel(msg: Union[list, discord.Message], sec: int):
    await sleep(sec)
    try:
        if isinstance(msg, list):
            for elm in msg:
                await discord.Message.delete(elm)
        else:
            await discord.Message.delete(msg)
    except Exception:
        return

# generate captcha code for claim
def captcha_create() -> str:
    global WD

    chars = string.ascii_uppercase + string.digits
    i = 0
    code = ""
    while i < 5:
        chce = random.choice(chars)
        code += chce
        i += 1
    img = ImageCaptcha(fonts=[path(WD, "src", "font", "VCR_OSD_MONO.ttf")])
    imgPath = path(WD, "src", "data", code + ".png")
    img.write(code, imgPath)

    print(code)

    return imgPath, code

# random drop algorithm
async def dropEvent():
    global WD, captchaData, emojis, delete_after

    await sleep(delete_after["drop"])

    while 1:
        msg = []
        imgPath = ""
        code = ""
        guildData = loadCompletGuilds()
        tmpc = cardLoader()

        if tmpc["n1"] == {} and tmpc["n2"] == {} and tmpc["n3"] == {} and tmpc["n4"] == {} and tmpc["n5"] == {}:
            await sleep(1)
            continue

        for guild in guildData.values():
            if guild["channels"] != [] and guild["status"] and client.get_guild(int(guild["id"])) is not None:
                card, chan = cardSelector(guild["channels"])
                chan:discord.TextChannel = client.get_channel(chan)
                emb = discord.Embed(title=card["name"], url=card["url"], description="**Level:** {}\n**Anime:** *{}*\n`{}claim [captcha code]`".format((emojis["star"]+" ") * card["lvl"] + (emojis["nostar"]+" ") * (5 - card["lvl"]), card["anime"], client.command_prefix), color=0x8AF6FF)
                emb.set_image(url=card["url"])
                msg.append(await chan.send(embed=emb, delete_after=delete_after["drop"]))
                imgPath, code = captcha_create()
                file = discord.File(imgPath)
                msg.append(await chan.send("", file=file, delete_after=delete_after["drop"]))
                captchaData[str(chan.guild.id) + str(chan.id)] = {"code":code, "msg":msg.copy(), "path":imgPath, "card":card.copy()}

        await sleep(int(delete_after["drop"]))

        try:
            if msg != []:
                captchaData[str(msg[0].guild.id) + str(msg[0].channel.id)] = {"code":"", "msg":"", "path":"", "card":""}
            os.remove(imgPath)
        except Exception:
            pass



# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #



# confirm the bot is ready
@client.event
async def on_ready():
    print("target: {0.user}".format(client))
    await dropEvent()






# -------------------------------------------------------------------------------------------------------------------------- #
#                                                       ADMIN COMMANDS                                                       #
# -------------------------------------------------------------------------------------------------------------------------- #

# set channel allowed for dropEvent
@client.command(name="channel")
@commands.has_permissions(administrator=True)
async def setChannel(ctx, option="", channels: commands.Greedy[discord.TextChannel]=""):
    global WD, delete_after

    await discord.Message.delete(ctx.message)
    cmmd_help = "`{}channel   [optional: [add|remove|reset]]   [add|remove: <channel_mention>]`".format(client.command_prefix)

    guildId = str(ctx.guild.id)

    if isinstance(channels, str) and option != "reset" and option != "":
        await ctx.send(ctx.author.mention + " `channel` non mentionné(s). " + cmmd_help,delete_after=delete_after["error"])
        return

    if option == "":
        guildData = loadGuildData(guildId)
        embLst = []
        emb = discord.Embed(title="Liste des channels:", color=0xd5d5d5)
        emb.description = ""
        if guildData["channels"] != []:
            i = 0
            p = 1
            for c in guildData["channels"]:
                if i == 10:
                    embLst.append(emb)
                    p += 1
                    emb = discord.Embed(title="Liste des channels:", description="*Part. {}*\n\u200B\n".format(p), color=0xd5d5d5)
                    i = 0
                emb.description += "• `{}`\n".format(client.get_channel(c))
                i += 1
        if emb.description == "":
            emb.description = "• *Aucun channel ajouté.*"
        embLst.append(emb)
        emb = embLst[0]
        msg:discord.Message = await ctx.send(embed=emb)
        card_reactId = str(ctx.author.id) + "_" + str(msg.id)
        if len(embLst) > 1:
            pages[card_reactId] = {"embed":embLst, "index":0}
            for e in ["▶️", "⏩", "✖️"]:
                await msg.add_reaction(e)
        else:
            await msg.add_reaction("✖️")
            pages[card_reactId] = {}
    elif option == "add":
        guildData = loadGuildData(guildId)
        added = ""
        for channel in channels:
            if not channel.id in guildData["channels"]:
                guildData["channels"].append(channel.id)
                saveGuildData(guildData)
                added += "channel enregistré `{}`\n".format(channel.name)
            else:
                added += "`{}` est déjà enregistré.\n". format(channel.name)
        await ctx.send(ctx.author.mention + "\n" + added, delete_after=delete_after["validating"])
    elif option == "remove":
        guildData = loadGuildData(guildId)
        removed = ""
        for channel in channels:
            if channel.id in guildData["channels"]:
                i = 0
                while i < len(guildData["channels"]):
                    if guildData["channels"][i] == channel.id:
                        del guildData["channels"][i]
                        break
                    i += 1
                del i
                saveGuildData(guildData)
                removed += "channel supprimé `{}`\n".format(channel.name)
            else:
                removed += "`{}` n'est pas dans la liste des channels.\n".format(channel.name)
        await ctx.send(ctx.author.mention + "\n" + removed, delete_after=delete_after["validating"])
    elif option == "reset":
        emb = discord.Embed(title="Reset la liste des channels ?", description="Êtes-vous sûr de vouloir remettre à 0\nla liste des channels autorisés pour le drop de carte ?", color=0xd5d5d5)
        msg = await ctx.send(embed=emb)
        for emoji in ["✔", "❌"]:
            await msg.add_reaction(emoji)
        guildData = loadGuildData(guildId)
        guildData["reac_id"] = {str(msg.id):str(ctx.author.id)}
        saveGuildData(guildData)
        await tmpChoice(guildId, 30)
    else:
        await ctx.send(ctx.author.mention + " option inconnu.\n`{}channel [add|remove|reset] [add|remove: <channel_mention>]`".format(client.command_prefix), delete_after=delete_after["error"])

# called if an error is raised in setChannel
@setChannel.error
async def setChannel_error(ctx, error):
    global delete_after

    print_traceback(error)



# launch/stop the dropEvent
@client.command(name="drop")
@commands.has_permissions(administrator=True)
async def drop(ctx, arg):
    global WD, delete_after

    await discord.Message.delete(ctx.message)

    guildId = str(ctx.guild.id)
    empty_dict = True

    guildData = loadGuildData(guildId)
    if arg == "start":
        if not guildData["status"]:
            for section in cardLoader().values():
                if section != {}:
                    empty_dict = False
                    break
            if not empty_dict:
                guildData["status"] = True
                stats = "Drop lancé"
            else:
                await ctx.send(ctx.author.mention + " vous ne pouvez pas démarrer le drop event car aucune carte n'a encore été ajoutée.", delete_after=delete_after["error"])
                return
        else:
            stats = "Le drop est déjà lancé."
    elif arg == "stop":
        if guildData["status"]:
            guildData["status"] = False
            stats = "Drop arrêté."
        else:
            stats = "Le drop est déjà arrêté."
    else:
        await ctx.send(ctx.author.mention + " drop option inconnu: `{}drop [start|stop]`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    await ctx.send(stats, delete_after=delete_after["validating"])
    saveGuildData(guildData)

# called if an error is raised in drop
@drop.error
async def drop_error(ctx, error):
    global delete_after

    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(ctx.author.mention + " argument manquant: \n`{}drop [start|stop]`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# check if the user is in guild
def is_in_guild(guilds_id):
    async def check_guild(ctx:commands.Context):
        return ctx.guild.id in guilds_id
    return commands.check(check_guild)

# set authorized user to call the command
def authorized_user(user_id):
    async def check_user(ctx:commands.Context):
        return ctx.author.id in user_id
    return commands.check(check_user)

# $card [add|remove|edit] <card_id> [optional add|edit: name=Exemple Card anime=Exemple Card Adventure url=<direct_url> lvl=0]
# card parser: CRUD manager for cards
@client.command(name="card", aliases=["c"])
@commands.has_permissions(administrator=True)
@is_in_guild([..., ...])
async def card_manager(ctx:commands.Context, option, card_id="", *stats):
    global WD, emojis, delete_after

    name, id, anime, url, lvl, claim = "", "", "", "", "", ""

    if card_id == "" and option != "show":
        await ctx.send(ctx.author.mention + " argument manquant: `{}card [add|remove|edit|show] [add|remove|edit|(optional for show): <card_id>] [add|edit: name=Exemple Card anime=Exemple Card Adventure url=<direct_url> lvl=0 [optional: claim=False]]`".format(client.command_prefix), delete_after=delete_after["error"])
        return

    card = get_card(card_id) # get card and check if card exist
    if "=" in card_id:
        await ctx.send(ctx.author.mention + " `card_id` n'a pas été défini.", delete_after=delete_after["error"])
        return

    if card is None and ((option != "add" and option != "show") or (card_id != "" and option == "show")): # if card not exist and the command is not $card add
        await ctx.send(ctx.author.mention + " ce `card_id` n'existe pas.", delete_after=delete_after["error"])
        return

    def notOther(param):
        if "=" in param:
            return False
        return True
    
    def return_arg(param:tuple, startP:list, i:int):
        p = startP[1]
        while i < len(param):
            if notOther(param[i]):
                p += " " + param[i]
            else:
                break
            i += 1
        return p

    if option == "add" or option == "edit":
        if card is not None and option == "add": # if trying to add a existing card
            await ctx.send(ctx.author.mention + " cette carte existe déjà.", delete_after=delete_after["error"])
            return
        parserStart=("name=", "anime=", "url=", "lvl=", "claim=")
        if option == "add":
            id = sepChar(card_id, " '\"/\\?;:.^,}{][)(+=°|`<>", "_")
        else:
            id = card_id
        load_embed = discord.Embed(title="Vérification des arguments . . .", description="*Cette action peut prendre plusieurs secondes.*")
        loading_msg = await ctx.send(embed=load_embed)
        i = 0
        while i < len(stats):
            if stats[i].startswith(parserStart):
                startP = stats[i].split("=")
                if startP[0] == "name" and name == "":
                    name:str = return_arg(stats, startP, i+1).capitalize()
                if startP[0] == "anime" and anime == "":
                    anime = return_arg(stats, startP, i+1)
                if startP[0] == "url" and url == "":
                    url = return_arg(stats, startP, i+1)
                    try:
                        test_r = requests.get(url=url)
                        if b"<html>" in test_r.content or b"<!DOCTYPE html>" in test_r.content or b"<html" in test_r.content:
                            await ctx.send(ctx.author.mention + " l'`url` n'est pas un lien direct vers l'image.", delete_after=delete_after["error"])
                            await discord.Message.delete(loading_msg)
                            return
                        del test_r
                    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
                        await ctx.send(ctx.author.mention + " le schema de l'`url` est incorrect.", delete_after=delete_after["error"])
                        await discord.Message.delete(loading_msg)
                        return
                    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
                        await ctx.send(ctx.author.mention + " connection impossible, la page n'existe peut-être pas ou l'`url` est erroné.", delete_after=delete_after["error"])
                        await discord.Message.delete(loading_msg)
                        return
                if startP[0] == "lvl" and lvl == "":
                    try:
                        lvl = int(return_arg(stats, startP, i+1))
                    except ValueError:
                        await ctx.send(ctx.author.mention + " le paramètre `lvl` doit être un chiffre.", delete_after=delete_after["error"])
                        await discord.Message.delete(loading_msg)
                        return
                    if lvl not in range(1, 6):
                        await ctx.send(ctx.author.mention + " le paramètre `lvl` doit être un chiffre entre 1 et 5.", delete_after=delete_after["error"])
                        await discord.Message.delete(loading_msg)
                        return
                if startP[0] == "claim" and claim == "":
                    claim = return_arg(stats, startP, i+1)
                    if claim.lower() == "false":
                        claim = False
                    elif claim.lower() == "true":
                        claim = True
                    else:
                        await ctx.send(ctx.author.mention + " le paramètre `claim` doit être `true` ou `false`. *(`true` = Oui | `false` = Non)*", delete_after=delete_after["error"])
                        await discord.Message.delete(loading_msg)
                        return
            i += 1

        if (name == "" or anime == "" or url == "" or lvl == "") and option == "add":
            missing_args = []
            if name == "":
                missing_args.append("name")
            if anime == "":
                missing_args.append("anime")
            if url == "":
                missing_args.append("url")
            if lvl == "":
                missing_args.append("lvl")
            await ctx.send(ctx.author.mention + " argument manquant: {}.".format(", ".join(missing_args)), delete_after=delete_after["error"])
            return
        cards = cardLoader()
        
        lvl = lvl if lvl != "" else card["lvl"]
        str_lvl = "n{}".format(lvl if option == "add" else card["lvl"])
        name = name if name != "" else cards[str_lvl][id]["name"]
        anime = anime if anime != "" else cards[str_lvl][id]["anime"]
        url = url if url != "" else cards[str_lvl][id]["url"]

        if claim != "" and lvl not in range(4, 6):
            await ctx.send(ctx.author.mention + " le paramètre `claim` est réservé aux cartes de niveau 4 et 5.", delete_after=delete_after["error"])
            await discord.Message.delete(loading_msg)
            return

        str_lvl = "n{}".format(lvl)
        if option == "edit":
            previous_lvl = "n{}".format(card["lvl"])
        else:
            previous_lvl = lvl

        cards[str_lvl][id] = {}

        cards[str_lvl][id]["name"] = name
        cards[str_lvl][id]["id"] = id
        cards[str_lvl][id]["anime"] = anime
        cards[str_lvl][id]["url"] = url
        cards[str_lvl][id]["lvl"] = lvl
        if claim != "" and option == "add":
            cards[str_lvl][id]["claimed"] = claim
            cards[str_lvl][id]["user"] = 0

        if option == "edit":
            if "claimed" in card.keys():
                cards[str_lvl][id]["claimed"] = card["claimed"] if claim == "" else claim
                cards[str_lvl][id]["user"] = card["user"]
                if claim == False:
                    if cards[previous_lvl][id]["user"] != 0:
                        cU = userAccount(client.get_user(cards[previous_lvl][id]["user"]))
                        del cU.cards[previous_lvl][id]
                        cU.save()
                        cards[str_lvl][id]["user"] = 0

        if lvl >= 4:
            cards[str_lvl][id]["claimed"] = cards[str_lvl][id]["claimed"] if "claimed" in cards[str_lvl][id].keys() else False
            cards[str_lvl][id]["user"] = cards[str_lvl][id]["user"] if "user" in cards[str_lvl][id].keys() else 0
        elif "claimed" in cards[str_lvl][id].keys():
            del cards[str_lvl][id]["claimed"]
            if cards[previous_lvl][id]["user"] != 0:
                cU = userAccount(client.get_user(cards[previous_lvl][id]["user"]))
                del cU.cards[previous_lvl][id]
                cU.save()
            del cards[str_lvl][id]["user"]

        if option == "edit":
            if str_lvl != previous_lvl:
                del cards[previous_lvl][id]
        with open(path(WD, "src", "cards_links.json"), "w") as data:
            json.dump(cards, data, indent=4)
            
        emb = discord.Embed(title="{}".format(name), url=url, description="\n• **Anime:** *{}*\n• **Id**: `{}`\n".format(anime, id), color=0x93abff)
        if option == "add":
            emb.set_author(name="Set card:", icon_url=ctx.author.avatar_url)
        if option == "edit":
            emb.set_author(name="Edit card:", icon_url=ctx.author.avatar_url)
            if lvl >= 4:
                card_user = client.get_user(cards[str_lvl][id]["user"])
                if card_user is not None:
                    by_show = card_user.name
                elif cards[str_lvl][id]["claimed"] is False:
                    by_show = "Nobody"
                else:
                    by_show = "Unknow user"
                emb.set_footer(text="Claimed:  {}   [by:  {}]".format("Yes" if cards[str_lvl][id]["claimed"] else "No", by_show), icon_url=url)
            emb.add_field(name="\u200B", value="{}".format(emojis["star"] * lvl + emojis["nostar"] * (5 - lvl)))
        emb.set_image(url=url)
        await discord.Message.delete(loading_msg)
        msg = await ctx.send(embed=emb)
        await msg.add_reaction("✖️")
        card_reactId = str(ctx.author.id) + "_" + str(msg.id)
        pages[card_reactId] = {}
        allGuilds = loadCompletGuilds()
        if option == "edit":
            card = cards[str_lvl][id]
            for guild in allGuilds.values():
                shop_card = getShopCard(card["id"], guild["id"])
                if shop_card is not None:
                    guild["shop"]["cards"][shop_card["index"]]["name"] = card["name"]
                    guild["shop"]["cards"][shop_card["index"]]["anime"] = card["anime"]
                    guild["shop"]["cards"][shop_card["index"]]["url"] = card["url"]
                    guild["shop"]["cards"][shop_card["index"]]["lvl"] = card["lvl"]
                    saveGuildData(guild)
    elif option == "remove":
        await discord.Message.delete(ctx.message)
        cards = cardLoader()
        allGuilds = loadCompletGuilds()
        for guild in allGuilds.values():
            shop_card = getShopCard(card["id"], guild["id"])
            if shop_card is not None:
                guild["shop"]["cards"][shop_card["index"]] = {}
                saveGuildData(guild)
        del cards["n" + str(card["lvl"])][card["id"]]
        with open(path(WD, "src", "cards_links.json"), "w") as data:
            json.dump(cards, data, indent=4)
        await ctx.send(ctx.author.mention + " `"+ card["name"] +"` deleted.", delete_after=delete_after["validating"])
    elif option == "show":

        await discord.Message.delete(ctx.message)

        if card is not None:
            emb = discord.Embed(title="{}".format(card["name"]), description=" • **anime:** *{}*\n • **id:** `{}`".format(card["anime"], card["id"]), url=card["url"], color=0x93abff)
            emb.add_field(name="\u200B", value="{}".format((emojis["star"] * card["lvl"]) + (emojis["nostar"] * (5 - card["lvl"]))))
            emb.set_image(url=card["url"])
            emb.set_author(name="Show card:", icon_url=ctx.author.avatar_url)
            if 'claimed' in card.keys():
                card_user = client.get_user(card["user"])
                if card_user is not None:
                    by_show = card_user.name
                elif card["claimed"] is False:
                    by_show = "Nobody"
                else:
                    by_show = "Unknow user"
                emb.set_footer(text="Claimed: {}   [by:  {}]".format("Yes" if card["claimed"] else "No", by_show), icon_url=card["url"])
            msg = await ctx.send(embed=emb)
            await msg.add_reaction("✖️")
            card_reactId = str(ctx.author.id) + "_" + str(msg.id)
            pages[card_reactId] = {}
            return

        cards = cardLoader()
        f = 0
        part = 1
        emb = discord.Embed(title=emojis["card"] + "   •   __Liste des cartes:__   •   " + emojis["card"], description="*Liste des cartes présentes dans la base de données:*\n", color=0x93abff)
        embLst = []
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        for nx in cards.items():
            for card in nx[1].values():
                if not f < 12:
                    f = 0
                    part += 1
                    embLst.append(emb)
                    emb = discord.Embed(title=emojis["card"] + "   •   __Part. {}:__   •   ".format(part) + emojis["card"], description="\u200B", color=0x93abff)
                if nx[0] == "n4" or nx[0] == "n5":
                    claimed = "❗️" if card["claimed"] else ""
                else:
                    claimed = ""
                name = emojis["card"] + claimed + " • __{}__".format(card["name"])
                val = "\u200B \u200B \u200B \u200B \u200B \u200B \u200B • **id:** [{}]({})".format(card["id"], card["url"]) + "\n\u200B \u200B \u200B \u200B \u200B \u200B \u200B • {}★".format(card["lvl"])
                emb.add_field(name=name, value=val, inline=True)
                f += 1
            rest = 3 - (len(nx[1]) % 3)
            if rest < 3:
                i = 0
                while i < rest:
                    emb.add_field(name="\u200B", value="\u200B", inline=True)
                    f += 1
                    i += 1
            if f+1 < 12 and nx[0] != "n5":
                emb.add_field(name="\u200B", value="\u200B", inline=False)
                f += 1
        if embLst != []:
            embLst.append(emb)
            emb = embLst[0]
            msg:discord.Message = await ctx.send(embed=emb)
            card_reactId = str(ctx.author.id) + "_" + str(msg.id)
            pages[card_reactId] = {"embed":embLst, "index":0}
            for e in ["▶️", "⏩", "✖️"]:
                await msg.add_reaction(e)
        else:
            msg = await ctx.send(embed=emb)
            await msg.add_reaction("✖️")
            card_reactId = str(ctx.author.id) + "_" + str(msg.id)
            pages[card_reactId] = {}
    else:
        await ctx.send(ctx.author.mention + " argument manquant: `{}card [add|remove|edit] <card_id> [optional add|edit: name=Carte d'exemple anime=Aventure d'un exemple de carte url=<direct_url> lvl=0 [edit: claim=False]]`".format(client.command_prefix), delete_after=delete_after["error"])
        await discord.Message.delete(ctx.message)
    
    users_data = path(WD, "src", "data", "users")
    for user in os.listdir(users_data):
        no_finish = True
        user = user.split(".")[0]
        try:
            user = client.get_user(int(user))
        except ValueError:
            continue
        if user is not None:
            cU = userAccount(user)
            while no_finish:
                no_finish = False
                for nx in cU.cards.items():
                    for card in nx[1].values():
                        data_card = get_card(card["id"])
                        if data_card is not None:
                            if not card["name"] == data_card["name"]:
                                card["name"] = data_card["name"]
                            if not card["anime"] == data_card["anime"]:
                                card["anime"] = data_card["anime"]
                            if not card["url"] == data_card["url"]:
                                card["url"] = data_card["url"]
                            if not card["lvl"] == data_card["lvl"]:
                                card["lvl"] = data_card["lvl"]
                            cU.cards["n{}".format(card["lvl"])][card["id"]] = card.copy()
                        else:
                            no_finish = True
                            del cU.cards["n"+str(card["lvl"])][card["id"]]
                            break
            cU.save()

# called if an error is raised in card_manager
@card_manager.error
async def card_error(ctx:commands.Context, error):
    global delete_after

    if isinstance(error, commands.errors.MissingRequiredArgument):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " argument manquant: `{}card [add|remove|edit] <card_id> [optional add|edit: name=Carte d'exemple anime=Aventure d'un exemple de carte url=<direct_url> lvl=0 [edit: claim=False]]`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# set bot prefix
@client.command(name="prefix", aliases=["p"])
@commands.has_permissions(administrator=True)
@authorized_user([..., ...])
async def prefix_edit(ctx: commands.Context, prefix):
    global delete_after

    chars_letters = string.ascii_letters
    chars_digits = string.digits
    illegal = string.whitespace
    chars = chars_letters + chars_digits + illegal
    letter = False
    digit = False

    if len(prefix) > 3:
        await ctx.send(ctx.author.mention + " le prefix ne peut pas avoir plus de 3 caractères.", delete_after=delete_after["error"])
        return
    if prefix in chars:
        await ctx.send(ctx.author.mention + " ce caractère ne peut pas être utilisé seul.", delete_after=delete_after["error"])
        return
    for p in prefix:
        if p in chars_letters:
            letter = True
        if p in chars_digits:
            digit = True
        if p in illegal:
            await ctx.send(ctx.author.mention + " ce(s) caractère(s) ne peut pas être utilisé.", delete_after=delete_after["error"])
            return
    if letter and not digit:
        await ctx.send(ctx.author.mention + " le prefix doit contenir minimum 1 symbole.", delete_after=delete_after["error"])
        return
    client.command_prefix = prefix
    with open(path(WD, "src", "prefix"), "w") as data:
        data.write(prefix)
    await ctx.send(ctx.author.mention + " le prefix a été changé.", delete_after=delete_after["validating"])

# called if an error is raised in prefix_edit
@prefix_edit.error
async def prefix_error(ctx: commands.Context, error):
    pass






# -------------------------------------------------------------------------------------------------------------------------- #
#                                                       USERS COMMANDS                                                       #
# -------------------------------------------------------------------------------------------------------------------------- #

# CRUD shop manager for admin and shop displayer for users
@client.command(name="shop")
@commands.cooldown(1, 3, commands.BucketType.user)
async def shop(ctx: commands.Context, option="", card_id="", price="", index=""):
    global emojis, delete_after

    cmmd_error = "`{}shop [buy|show] <card_id>`".format(client.command_prefix)
    user = userAccount(ctx.author)
    await discord.Message.delete(ctx.message)

    if not option in ["buy", "show", "remove", "set"] and option != "":
        await ctx.send(ctx.author.mention + " option inconnu. `{}shop [buy|show|set] <card_id> [set: <price> <index range: 1-6>]`", delete_after=delete_after["error"])
        return

    if option != "":
        card = get_card(card_id)
        if card is not None:
            if option == "buy":
                buy_card = getShopCard(card["id"], ctx.guild.id)
                if buy_card is not None:
                    if user.money < buy_card["price"]:
                        await ctx.send(user.mention + " vous n'avez pas assez d'argent.", delete_after=delete_after["error"])
                        return
                    del user
                    if buy_card is not None:
                        await buyShopItem(ctx, emojis, buy_card)
                        await ctx.send(ctx.author.mention + " merci de votre achat !", delete_after=delete_after["validating"])
                    else:
                        await ctx.send(ctx.author.mention + " cette carte n'est pas dans le shop. " + cmmd_error, delete_after=delete_after["error"])
                else:
                    await ctx.send(ctx.author.mention + " cette carte n'est pas dans le shop. " + cmmd_error, delete_after=delete_after["error"])
            elif option == "show":
                show_card = getShopCard(card["id"], ctx.guild.id)
                if show_card is not None:
                    msg = await showShopItem(ctx, emojis, show_card)
                    await msg.add_reaction("✖️")
                    card_reactId = str(ctx.author.id) + "_" + str(msg.id)
                    pages[card_reactId] = {}
                else:
                    await ctx.send(ctx.author.mention + " cette carte n'est pas dans le shop. " + cmmd_error, delete_after=delete_after["error"])
            elif option == "set" and ctx.author.guild_permissions.administrator:
                if price != "" and index != "":
                    try:
                        price = int(price)
                        if not price >= 0:
                            await ctx.send(ctx.author.mention + " le prix ne peut pas être négatif. `{}shop [buy|show|set] <card_id> [set: <price> <index range: 1-6>]`".format(client.command_prefix), delete_after=delete_after["error"])
                        index = int(index)-1
                        if not index in range(0, 6):
                            raise ValueError
                        await setShop(ctx, card, price, index)
                        await ctx.send("Le shop a été mis à jour.", delete_after=delete_after["validating"])
                    except ValueError:
                        await ctx.send(ctx.author.mention + " l'option `price` ou `index` est incorrecte. `{}shop [buy|show|set] <card_id> [set: <price> <index range: 1-6>]`".format(client.command_prefix), delete_after=delete_after["error"])
                else:
                    await ctx.send(ctx.author.mention + " l'option `price` ou `index` est manquante. `{}shop [buy|show|set] <card_id> [set: <price> <index range: 1-6>]`".format(client.command_prefix), delete_after=delete_after["error"])
            elif option == "remove" and ctx.author.guild_permissions.administrator:
                rem_card = getShopCard(card["id"], ctx.guild.id)
                if rem_card is not None:
                    await removeShopCard(ctx, rem_card)
                    await ctx.send(ctx.author.mention + " `{}` supprimé.".format(rem_card["name"]), delete_after=delete_after["validating"])
                else:
                    await ctx.send(ctx.author.mention + " cette carte n'est pas dans le shop. " + cmmd_error, delete_after=delete_after["error"])
        else:
            await ctx.send(ctx.author.mention + " carte non trouvé. " + cmmd_error, delete_after=delete_after["error"])
    else:
        msg = await showShop(ctx, emojis)
        await msg.add_reaction("✖️")
        card_reactId = str(ctx.author.id) + "_" + str(msg.id)
        pages[card_reactId] = {}

# called if an error is raised in shop
@shop.error
async def shop_error(ctx, error):
    global delete_after

    if isinstance(error, commands.errors.CommandOnCooldown):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " `{}shop` a 3 secondes de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# show user inventory
@client.command(name="inventory", aliases=["inv", "i"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def inventory(ctx, card_id=""):
    global WD, emojis, delete_after

    await discord.Message.delete(ctx.message)
    cU = userAccount(ctx.author)

    if card_id != "":
        idExst = False
        for cardKey in cU.cards.values():
            if card_id in cardKey.keys():
                idExst = True
                card = get_card(card_id, cU)
                emb = discord.Embed(title="{} `x{card_len}`".format(card["name"], card_len=card["nb"]), url=card["url"], description="\n• **Anime:** *{}*\n• **Id:** `{}`\n".format(card["anime"], card["id"]), color=0x8AF6FF)
                emb.set_author(name=cU.name, icon_url=cU.avatar_url)
                emb.add_field(name="\u200B", value="{}".format(emojis["star"] * card["lvl"] + emojis["nostar"] * (5 - card["lvl"])))
                emb.set_image(url=card["url"])
                msg = await ctx.send(embed=emb)
                await msg.add_reaction("✖️")
                card_reactId = str(ctx.author.id) + "_" + str(msg.id)
                pages[card_reactId] = {}
                return
        if not idExst:
            await ctx.send(cU.mention + " vous ne possédez pas cette carte.", delete_after=delete_after["error"])
            return
    else:
        emb = discord.Embed(title="💠   __Inventaire__   💠", color=0x8AF6FF)
        emb.set_author(name=cU.name, icon_url=cU.avatar_url)
        emb.set_footer(text="💠   {} [ i | inv | inventory ]   < card_id >".format(client.command_prefix))
        cardSize = 0
        for elm in cU.cards.values():
            for elm2 in elm:
                cardSize += elm[elm2]["nb"]
        del elm
        emb.add_field(name="\u200B", value="{money_emoji} • `Monnaie` • **{}**\n{card_emoji} • `Carte` • **{}**\n\u200B".format(cU.money, cardSize, money_emoji=emojis["money"], card_emoji=emojis["card"]), inline=False)
        f = 0
        i = 1
        line = 0
        inline = True
        embLst = []
        for nx in cU.cards.items():
            if nx[1] != {}:
                for c in nx[1].values():
                    if line == 2:
                        emb.add_field(name="\u200B", value="\u200B", inline=inline)
                        f+=1
                        line = 0
                    if not f < 12:
                        embLst.append(emb)
                        i += 1
                        f = 0
                        emb = discord.Embed(title="💠   __Inventaire__   💠", description="*Page {}:*\n\u200B".format(i), color=0x8AF6FF)
                        emb.set_author(name=cU.name, icon_url=cU.avatar_url)
                        emb.set_footer(text="💠   {} [ i | inv | inventory ]   < card_id >".format(client.command_prefix))
                    emb.add_field(name=emojis["card"]+" • **__{}__** `x{}` - {}★".format(c["name"], c["nb"], c["lvl"]), value="\u200B \u200B \u200B \u200B \u200B \u200B \u200B • **id:** [{}]({})".format(c["id"], c["url"]), inline=inline)
                    f += 1
                    line += 1
        rest = 3 - (f % 3)
        if rest != 0:
            i = 0
            while i < rest:
                emb.add_field(name="\u200B", value="\u200B", inline=inline)
                i += 1
        if embLst != []:
            embLst.append(emb)
            emb = embLst[0]
            msg:discord.Message = await ctx.send(embed=emb)
            card_reactId = str(ctx.author.id) + "_" + str(msg.id)
            pages[card_reactId] = {"embed":embLst, "index":0}
            for e in ["▶️", "⏩", "✖️"]:
                await msg.add_reaction(e)
        else:
            msg = await ctx.send(embed=emb)
            await msg.add_reaction("✖️")
            card_reactId = str(ctx.author.id) + "_" + str(msg.id)
            pages[card_reactId] = {}

# called if an error is raised in inventory
@inventory.error
async def inv_error(ctx: commands.Context, error):
    global delete_after

    if isinstance(error, commands.errors.CommandOnCooldown):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " `{}inventory` a 3 secondes de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# allow admin to give money to members
@client.command(name="give", aliases=["g"])
@commands.cooldown(1, 5, commands.BucketType.user)
async def give(ctx:commands.Context, user_mention:discord.Member, amount:int):
    global emojis, delete_after

    await discord.Message.delete(ctx.message)

    ctx_user = userAccount(ctx.author)
    user_mention = userAccount(user_mention)

    if not ctx.author.guild_permissions.administrator and ctx_user == user_mention:
        await ctx.send(ctx.author.mention + " vous ne pouvez pas vous donner de l'argent à vous-même.", delete_after=delete_after["error"])
        return

    if amount < 0:
        await ctx.send(ctx.author.mention + " le montant d'argent ne peut pas être négatif.", delete_after=delete_after["error"])
        return

    if ctx.author.guild_permissions.administrator:
        user_mention.money += amount
        user_mention.save()
        emb = discord.Embed(title=emojis["money"] + " • {} a ajouté `{}💎` à {}".format(ctx_user.name, amount, user_mention.name), description="{} a un total de `{}💎`".format(user_mention.mention, user_mention.money), color=0x50ea57)
        await ctx.send(embed=emb)
    else:
        if amount <= ctx_user.money:
            user_mention.money += amount
            ctx_user.money -= amount
            user_mention.save()
            ctx_user.save()
            emb = discord.Embed(title=emojis["money"] + " • {} a donné `{}💎` à {}".format(ctx_user.name, amount, user_mention.name), description="{} a un total de `{}💎`\n{} a un total de `{}💎`".format(user_mention.mention, user_mention.money, ctx_user.mention, ctx_user.money), color=0x50ea57)
            await ctx.send(embed=emb)
        else:
            await ctx.send(ctx.author.mention + " vous n'avez pas assez d'argent.", delete_after=delete_after["error"])

# called if an error is raised in give
@give.error
async def give_error(ctx:commands.Context, error):
    global delete_after

    await discord.Message.delete(ctx.message)
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(ctx.author.mention + " `{}give` a 3 secondes de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(ctx.author.mention + " arguement incconue. `{}give <user_mention> <money amount>`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.MemberNotFound):
        await ctx.send(ctx.author.mention + " utilisateur introuvable. `{}give <user_mention> <money amount>`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(ctx.author.mention + " le montant d'argent doit être un nombre.", delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# allow members to create an exchange request to an other member
@client.command(name="exchange", aliases=["ex"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def echange_card(ctx, user_mention: discord.Member, item_give, item_wanted): #echange <!@mention_user> card_id
    global emojis, exchange, delete_after

    user = userAccount(ctx.author)
    command_help = "`{}exchange <@user mention> [you: <card id>|<money amount>] [mentioned user: <card id>|<money amount>]`".format(client.command_prefix)

    if not user.is_exchange:
        if user.id == user_mention.id:
            await discord.Message.delete(ctx.message)
            await ctx.send(user.mention + " vous ne pouvez pas commencer un échange avec vous-même. " + command_help, delete_after=delete_after["error"])
            return
        user_mention = userAccount(user_mention)
        try:
            item_give = int(item_give)
            if not item_give >= 0:
                await ctx.send(user.mention + " l'argent que vous échangez ne peut pas être négatif. " + command_help)
                return
        except Exception:
            pass
        try:
            item_wanted = int(item_wanted)
            if not item_wanted >= 0:
                await ctx.send(user.mention + " l'argent que vous demandez ne peut pas être négatif. " + command_help)
                return
        except Exception:
            pass
        if isinstance(item_give, int) and isinstance(item_wanted, int):
            await ctx.send(user.mention + " vous ne pouvez pas échanger de l'argent.")
            return
        if isinstance(item_give, int) or isinstance(item_wanted, int):
            money:tuple = (item_give, "give") if isinstance(item_give, int) else (item_wanted, "wanted")
            if money[1] == "give":
                if money[0] > user.money:
                    await ctx.send(user.mention + " vous n'avez pas assez d'argent.", delete_after=delete_after["error"])
                    return
                ex_card = get_card(item_wanted, user_mention)
                if ex_card is None:
                    await discord.Message.delete(ctx.message)
                    await ctx.send(user.mention + " `card id` introuvable. " + command_help, delete_after=delete_after["error"])
                    return
                user1_card_field = emojis["money"] + " • **Monnaie** • `{}💎`\n".format(money[0]) + "• **Auteur:** `{author}`\n\u200B\n".format(author=user.name)
                user2_card_field = emojis["card"] + " • **[{}]({})**\n".format(ex_card["name"], ex_card["url"]) + "• **Auteur:** `{author}`\n• **Anime:** `{anime}`\n\u200B".format(author=user_mention.name, anime=ex_card["anime"])
            else:
                if money[0] > user_mention.money:
                    await ctx.send(user.mention + user_mention.name + " n'a pas assez d'argent.", delete_after=delete_after["error"])
                    return
                ex_card = get_card(item_give, user)
                if ex_card is None:
                    await discord.Message.delete(ctx.message)
                    await ctx.send(user.mention + " `card id` introuvable. " + command_help, delete_after=delete_after["error"])
                    return
                user2_card_field = emojis["money"] + " • **Monnaie** • `{}💎`\n".format(money[0]) + "• **Auteur:** `{author}`\n\u200B\n".format(author=user_mention.name)
                user1_card_field = emojis["card"] + " • **[{}]({})**\n".format(ex_card["name"], ex_card["url"]) + "• **Auteur:** `{author}`\n• **Anime:** `{anime}`\n\u200B".format(author=user.name, anime=ex_card["anime"])
            user.save()
            exchange_emoji = "🔁\n\u200B\n"
            item_give = money if isinstance(money[0], int) and money[1] == "give" else ex_card["id"]
            item_wanted = money if isinstance(money[0], int) and money[1] == "wanted" else ex_card["id"]
            footer = "{} id:   {}".format(ex_card["name"], ex_card["id"])
        else:
            gived_card = get_card(item_give, user)
            wanted_card = get_card(item_wanted, user_mention)
            if gived_card is not None and wanted_card is not None:
                user.save()
                user1_card_field = emojis["card"] + " • **[{}]({})**\n".format(gived_card["name"], gived_card["url"]) + "• **Auteur:** `{author}`\n• **Anime:** `{anime}`\n\u200B\n".format(author=user.name, anime=gived_card["anime"])
                exchange_emoji = "🔁\n\u200B\n"
                user2_card_field = emojis["card"] + " • **[{}]({})**\n".format(wanted_card["name"], wanted_card["url"]) + "• **Auteur:** `{author}`\n• **Anime:** `{anime}`\n\u200B".format(author=user_mention.name, anime=wanted_card["anime"])
                item_give = gived_card["id"]
                item_wanted = wanted_card["id"]
                footer = "{} id:   {}\n{} id:   {}".format(gived_card["name"], gived_card["id"], wanted_card["name"], wanted_card["id"])
            else:
                await discord.Message.delete(ctx.message)
                await ctx.send(user.mention + " `card id` introuvable. " + command_help, delete_after=delete_after["error"])
                return
        user.is_exchange = True
        emb = discord.Embed(title="⌛️ • {} a 60 secondes pour accepter • ⌛️".format(user_mention.name), user=user.name, colour=0xB2FF90, description="\n**Echange:**\n\u200B\n" + user1_card_field + exchange_emoji + user2_card_field)
        emb.set_author(name=user.name, icon_url=user.avatar_url)
        emb.set_footer(text=footer, icon_url=user_mention.avatar_url)
        msg = await ctx.send(embed=emb, delete_after=60.0)
        exchange[user.str_id + "_" + user_mention.str_id] = {"item_give":item_give, "by":user.id, "to":user_mention.id, "item_wanted":item_wanted, "msg":msg}
        await sleep(60)
        try:
            del exchange[user.str_id + "_" + user_mention.str_id]
            user = userAccount(ctx.author)
            user.is_exchange = False
            user.save()
        except Exception:
            pass
    else:
        await discord.Message.delete(ctx.message)
        await ctx.send(user.mention + " vous avez déjà commancé un échange.", delete_after=delete_after["error"])

# called if an error is raised in exchange_card
@echange_card.error
async def echange_error(ctx, error):
    global delete_after

    command_help = "`{}exchange <@user mention> <card id que vous échangez> <card id que vous attendez de l'utilisateur mentionné>`".format(client.command_prefix)

    if isinstance(error, commands.errors.MemberNotFound):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " utilisateur introuvable. " + command_help, delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " argument inconnu " + command_help, delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " `{}exchange` a 10 secondes de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# command for confirm exchange when an other member start the excahnge
@client.command(name="accept")
@commands.cooldown(1, 5, commands.BucketType.user)
async def accept_exchange(ctx: commands.Context, user_start_ex: discord.Member):
    global exchange, delete_after

    exchange_id = "_".join([str(user_start_ex.id), str(ctx.author.id)])
    if exchange_id in exchange.keys():
        if exchange[exchange_id]["msg"].channel.id == ctx.channel.id:
            user1 = userAccount(client.get_user(exchange[exchange_id]["by"]))
            user2 = userAccount(client.get_user(exchange[exchange_id]["to"]))
            tmpEmbed = exchange[exchange_id]["msg"]
            item_give = exchange[exchange_id]["item_give"]
            item_wanted = exchange[exchange_id]["item_wanted"]
            if isinstance(item_give, tuple) or isinstance(item_wanted, tuple):
                money = item_give if isinstance(item_give, tuple) else item_wanted
                user1.is_exchange = False
                user1.save()
                if money[1] == "give":
                    ex_card = get_card(item_wanted, user2)
                    user2.money += money[0]
                    user1.money -= money[0]
                    swapCards(user1, user2, ex_card)
                else:
                    ex_card = get_card(item_give, user1)
                    user1.money += money[0]
                    user2.money -= money[0]
                    swapCards(user2, user1, ex_card)
            else:
                card_user1 = get_card(exchange[exchange_id]["item_give"], user1) # {'url': '', 'id': '', 'anime': '', 'name': '', 'lvl': 0, 'nb': 0}
                card_user2 = get_card(exchange[exchange_id]["item_wanted"], user2)
                if card_user1["id"] == card_user2["id"]:
                    await ctx.send(user1.mention + user2.mention + " échange réussi.", delete_after=delete_after["validating"])
                else:
                    user1.is_exchange = False
                    user1.save()
                    swapCards(user1, user2, card_user2)
                    swapCards(user2, user1, card_user1)
            await ctx.send(user1.mention + user2.mention + " échange réussi.", delete_after=delete_after["validating"])
            try:
                await discord.Message.delete(tmpEmbed)
            except Exception:
                pass
            del exchange[exchange_id]
        else:
            await discord.Message.delete(ctx.message)
            await ctx.send(ctx.author.mention + " vous n'avez aucun échange en cours ici.", delete_after=delete_after["error"])
    else:
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " vous n'avez aucun échange en cours ici.", delete_after=delete_after["error"])

# called if an error is raised in accept_exchange
@accept_exchange.error
async def accept_error(ctx, error):
    global delete_after

    if isinstance(error, commands.errors.MissingRequiredArgument):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " `{}accept <mention user>`".format(client.command_prefix), delete_after=delete_after["error"])
        return
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await discord.Message.delete(ctx.message)
        await ctx.send(ctx.author.mention + " `{}accept` a 5 secondes de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return
    else:
        print_traceback(error)



# allow users to claim a dropped card
@client.command(name="claim")
@commands.cooldown(1, 1, commands.BucketType.user)
async def claim_card(ctx: commands.Context, arg):
    global WD, captchaData, delete_after

    await discord.Message.delete(ctx.message)

    guildId = str(ctx.guild.id)
    chanId = str(ctx.channel.id)

    if guildId+chanId in captchaData.keys():
        if arg.upper() == captchaData[guildId+chanId]["code"]:
            card = captchaData[guildId+chanId]["card"]
            if card["lvl"] in range(4, 6):
                tmpC = cardLoader()
                tmpC["n{}".format(card["lvl"])][card["id"]]["claimed"] = True
                tmpC["n{}".format(card["lvl"])][card["id"]]["user"] = ctx.author.id
                with open(path(WD, "src", "cards_links.json"), "w") as data:
                    json.dump(tmpC, data, indent=4)
            currentUser = userAccount(ctx.author)
            if card["id"] in currentUser.cards["n{}".format(card["lvl"])].keys():
                currentUser.cards["n{}".format(card["lvl"])][card["id"]]["nb"] += 1
            else:
                currentUser.cards["n{}".format(card["lvl"])][card["id"]] = card.copy()
                currentUser.cards["n{}".format(card["lvl"])][card["id"]]["nb"] = 1
            moneyWin = (card["lvl"] * card["lvl"]) * 20
            currentUser.money += moneyWin
            await ctx.send(ctx.author.mention + " félicitation, **" + card["name"] + "** fait maintenant parti(e) de votre inventire !"+
            "\n`+{}{}`".format(moneyWin, emojis["money"]),
            delete_after=delete_after["validating"])
            currentUser.save()
            os.remove(captchaData[guildId+chanId]["path"])
            for msg in captchaData[guildId+chanId]["msg"]:
                await discord.Message.delete(msg)
            captchaData[guildId+chanId] = {"code":"", "msg":"", "path":"", "card":""}
        else:
            await ctx.send(ctx.author.mention + " captcha incorrect.", delete_after=delete_after["validating"])
    else:
        await ctx.send("Aucune carte n'a drop ici.", delete_after=delete_after["validating"])

# called if an error is raised in claim_card
@claim_card.error
async def claim_error(ctx, error):
    global delete_after

    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(ctx.author.mention + " `{}claim` a 1 seconde de cooldown, veuillez patienter.".format(client.command_prefix), delete_after=delete_after["error"])
        return



# show all commands and chack if the request is doing by admin or user
@client.command(name="help", aliases=["h", "hlp"])
async def help_command(ctx: commands.Context):
    global delete_after

    await discord.Message.delete(ctx.message)

    emb = discord.Embed(title="❓   __Help__   ❓", description="\u200B", colour=0xFF8383)
    emb.set_author(name=str(ctx.author.name), icon_url=ctx.author.avatar_url)
    shop_admin = [emojis["user"] + " • " + "**{}shop   [optional:   [buy|show] <card_id>]**".format(client.command_prefix),
        "`shop` est la commande qui correspond la boutique et permet de la gérer.\n"+
        "• `buy:` permet à l'utilisateur d'cheter une carte présente dans le shop.\n"+
        "• `show:` affiche le contenu actuel du shop."]
    if ctx.author.guild_permissions.administrator:
        emb.add_field(name=emojis["admin"] + " • " + "**{}drop   [start|stop]**".format(client.command_prefix), value="*Description:*\n"+
            "`drop` est la commande qui gère l'activation ou l'arrêt du card drop. *(le drop périodique de carte)*\n"+
            "• `start:` démarre le card drop.\n"+
            "• `stop:` arrête le card drop.\n\u200B", inline=False)
        emb.add_field(name=emojis["admin"] + " • " + "**{}channel   [optional: [add|remove|reset]]   [add|remove: <channel_mention>]**".format(client.command_prefix), value="*Description:*\n"+
            "`channel` permet de gérer la liste des channels autorisés pour le card drop.\n"+
            "• `add:` ajoute le ou les channel(s) mentionné(s) à la liste des channels dans lesquels le drop card est autorisé.\n"+
            "• `remove:` supprime le ou les channel(s) mentionné(s) à la liste des channels dans lesquels le drop card est autorisé.\n"+
            "• `reset:` remet à 0 la liste des channels.\n"+
            "• • `<channel_mention>:` le channel mentionné.\n**Exemple:** `#exemple-chan`.\n\u200B", inline=False)
        shop_admin = [emojis["admin"] + " • " + "**{}shop [optional: [buy|show|set] <card_id> [set: <price> <index>]]**".format(client.command_prefix),
        shop_admin[1] + "\n• `remove:` permet aux administrateurs de retirer une carte présente dans le shop."+
        "\n• `set:` permet aux administrateurs d'ajouter une carte existante dans le shop."+
        "\n• • `<price>`: le prix de la carte dans le shop."+
        "\n• • `<index>: entre 1-5`: la place de la carte dans le shop."]
        emb.add_field(name=emojis["admin"] + " • " + "**{}card   [add|remove|edit|show]   [add|remove|edit|show:   <card_id>(show peut être appelé sans donner de card id)]   [add|edit: name, anime, url, lvl [optional: claim]]**".format(client.command_prefix),
        value="`card` sert à ajouter, retirer, éditer ou montrer une carte dans la base de données, il dispose d'un parser donc d'un format d'écriture particulier que vous pouvez retrouver dans l'exemple.\n"+
        "• `add:` permet d'ajouter une carte **INEXISTANTE** à la base de données. options: `<card_id>` `name`, `anime`, `url`, `lvl` [le format d'utilisation est dans l'exemple].\n"+
        "• `remove:` permet de supprimer une carte de la base de données. options: `<card_id>`\n" +
        "• `edit:` permet d'éditer une carte existante. options: `<card_id>` `name`, `anime`, `url`, `lvl` [le format d'utilisation est dans l'exemple].\n" +
        "• `show:` permet d'afficher une carte présente dans la base de données. options: `<card_id>` (l'option `card_id` est optionnel ici, vous pouvez utiliser `{}card show` pour voir toutes les cartes présentes dans la base de données).\n".format(client.command_prefix), inline=False)
        emb.add_field(name="**Explication des parametrès:**", value=
        "• • `<card_id>:` l'id d'une carte dans la base de données. (pour l'option `add`, l'id de la carte doit être un id inexistant).\n"+
        "• • `<name>:` le nom de la carte.\n"+
        "• • `<anime>:` l'animé d'où provient le sujet de la carte.\n"+
        "• • `<url>:` le **lien direct** vers l'image de la carte (l'image de la carte a besoin d'être upload quelque part).\n"+
        "• • `<lvl>:` le niveau de la carte. (entre 1 - 5)\n"+
        "• • optional: `<claim>:` le status de claim de la carte. (claim=true|claim=false)\n\u200B\n"+
        "**Exemple:** `{}card add|edit <card_id> name=Exemple Card anime=Exemple Card Adventure url=<direct_url> lvl=0 claim=False`\n\u200B".format(client.command_prefix), inline=False)
        if authorized_user(ctx.author.id):
            emb.add_field(name="🔐 • **{}[p|prefix] <new_prefix>**".format(client.command_prefix), value="*Description:*\n"+
            "`prefix` permet de changer le prefix général du bot. *(actuellement: `{}`)*\n".format(client.command_prefix)+
            "• `<new_prefix>:` le nouveau prefix du bot.\n\u200B", inline=False)
    shop_admin[1] += "\n• • `<card_id>:` l'id d'une carte présente dans le shop."
    emb.add_field(name=shop_admin[0], value="*Description:*\n" + shop_admin[1] + "\n\u200B", inline=False)
    emb.add_field(name=emojis["user"] + " • " + "**{}[i|inv|inventory]   <Optional: card_id>**".format(client.command_prefix), value="*Description:*\n"+
        "`inventory` est la commande de l'inventaire, elle permet d'en montrer l'intégralité ou juste d'en montrer une carte en complétant l'option `card_id`.\n"+
        "• `<card_id>:` l'id de la carte que vous voulez afficher depuis votre inventaire.\n\u200B", inline=False)
    emb.add_field(name=emojis["user"] + " • " + "**{}give   <user_mention>   <amount>**".format(client.command_prefix), value="*Description:*\n"+
        "`give` permet de donner un certain montant d'argent à un membre du serveur.\n"+
        "• `<user_mention>:` la mention d'un membre du serveur. *(exemple: **@Tom#1234**)*\n"+
        "• `<amount>:` le montant d'argent que vous donnez.\n\u200B", inline=False)
    emb.add_field(name=emojis["user"] + " • " + "**{}[ex|exchange]   <@user_mention>   <your_card_id>   <his_card_id>**".format(client.command_prefix), value="*Description:*\n"+
        "`exchange` permet d'échanger une de vos cartes avec un autre membre du serveur.\n"+
        "• `<@user_mention>:` la mention d'un membre du serveur. *(exemple: **@Ulss74#1234**)*\n"+
        "• `<your_card_id>:` l'id de la carte dans votre inventaire que vous voulez échanger.\n"+
        "• `<his_card_id>:` l'id de la carte dans l'inventaire du membre mentionné qu'il veut échanger.\n\u200B"
        , inline=False)
    emb.add_field(name=emojis["user"] + " • " + "**{}accept   <@user mention>**".format(client.command_prefix), value="**[SEULEMENT PENDANT UN ECHANGE]**\n*Description:*\n"+
        "`accept` rejoint la commande `exchange` et permet au membre du serveur mentionné dans l'échange précédemment commencé (s'i y en a un) de l'accepter. *(si l'échange ne vous convient pas n'acceptez tout simplement pas, l'échange s'annulera automatiquement après 60 secondes)*\n"+
        "• `<@user mention>:` la mention d'un membre du serveur. *(exemple: **@{}#{}**)*\n".format(client.user.name,client.user.discriminator), inline=False)
    msg = await ctx.send(embed=emb)
    await msg.add_reaction("✖️")
    card_reactId = str(ctx.author.id) + "_" + str(msg.id)
    pages[card_reactId] = {}

# called if an error is raised in help_command
@help_command.error
async def help_error(ctx: commands.Context, error):
    global delete_after

    print_traceback(error)



# if an unknow error is raised
@client.event
async def on_command_error(ctx, error):
    global delete_after

    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print_traceback(error)



# -------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                            #
# -------------------------------------------------------------------------------------------------------------------------- #






# called for each message
@client.event
async def on_message(message:discord.Message):
    global WD, captchaData

    if message.author.bot:
        return

    guildId = str(message.guild.id)

    guildData = loadGuildData(guildId)
    if guildData is None:
        guildData = json.loads(exst(path(WD, "src", "templates", "guild_template.json")))
        guildData["id"] = guildId
        saveGuildData(guildData)
    
    cU = userAccount(message.author)

    if not message.content.startswith(client.command_prefix):
        cU.money += 1
        cU.save()

    await client.process_commands(message)



# called for each reaction added
@client.event
async def on_reaction_add(reaction:discord.Reaction, user:discord.Member):
    global WD, captchaData

    if user.bot:
        return

    guildId = str(user.guild.id)
    userId = str(user.id)
    
    guildData = loadGuildData(guildId)

    # reac: reset channel list
    if reaction.emoji in ["✔", "❌"] and userId == guildData["reac_id"][str(reaction.message.id)]:
        if str(reaction.emoji) == "✔":
            await discord.Message.delete(reaction.message)
            guildData["channels"] = list()
            del guildData["reac_id"]
            saveGuildData(guildData)
            await reaction.message.channel.send(user.mention + " The channels list has been reset !", delete_after=delete_after["validating"])
        if str(reaction.emoji) == "❌":
            await discord.Message.delete(reaction.message)
            del guildData["reac_id"]
            saveGuildData(guildData)
    
    if reaction.emoji in ["⏪", "◀️", "▶️", "⏩", "✖️"]:
        await reaction.remove(user)
        card_reactId = str(user.id) + "_" + str(reaction.message.id)
        if card_reactId in pages.keys():
            if reaction.emoji == "✖️":
                await discord.Message.delete(reaction.message)
                del pages[card_reactId]
                return
            if reaction.emoji == "▶️":
                pages[card_reactId]["index"] += 1
            if reaction.emoji == "◀️":
                pages[card_reactId]["index"] -= 1
            if reaction.emoji == "⏪":
                pages[card_reactId]["index"] = 0
            if reaction.emoji == "⏩":
                pages[card_reactId]["index"] = len(pages[card_reactId]["embed"])-1

            await reaction.message.edit(embed=pages[card_reactId]["embed"][pages[card_reactId]["index"]])
            await reaction.message.clear_reactions()
            if pages[card_reactId]["index"] == 0:
                for e in ["▶️", "⏩", "✖️"]:
                    await reaction.message.add_reaction(e)
            elif pages[card_reactId]["index"] == len(pages[card_reactId]["embed"])-1:
                for e in ["⏪", "◀️", "✖️"]:
                    await reaction.message.add_reaction(e)
            else:
                for e in ["⏪", "◀️", "▶️", "⏩", "✖️"]:
                    await reaction.message.add_reaction(e)
        elif user.guild_permissions.administrator:
            if reaction.emoji == "✖️":
                await discord.Message.delete(reaction.message)
                for elm in pages.items():
                    if str(reaction.message.id) in elm[0]:
                        del pages[elm[0]]
                        return
                return



# start the bot
def startClient():
    client.run(token)

# chack il the file is directly run
if  __name__ == "__main__":
    startClient()