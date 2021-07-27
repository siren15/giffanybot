import discord
import pymongo
from pymongo import MongoClient
from mongo import *
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from datetime import datetime
from discord.ext import commands

class ModuleNotActivatedInGuild(commands.CheckFailure):
        pass

class EventNotActivatedInGuild(commands.CheckFailure):
        pass

class CommandNotActivatedInGuild(commands.CheckFailure):
        pass

class NotGuild(commands.CheckFailure):
        pass

class UserInBlacklist(commands.CheckFailure):
        pass

class missing_role(commands.CheckFailure):
        pass

def isguild(guild, guildid):
    if guild.id != guildid:
        raise NotGuild(f'not activated for {guild}')
    return True

def iscogactive(guild, cog: str):
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['prefixes']
    cogs = table.find({"guildid":guild.id})
    for c in cogs:
        if cog.lower() not in c['activecogs'].lower():
            raise ModuleNotActivatedInGuild(f"[{datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}]{cog} not activated for {guild}")
        return True

def is_event_active(guild, event: str):
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['prefixes']
    events = table.find({"guildid":guild.id})
    for e in events:
        if event.lower() not in e['activecommands'].lower():
            raise EventNotActivatedInGuild(f'{event} not activated for {guild}')
        return True

def has_active_cogs(cog: str):
    async def predicate(ctx):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['prefixes']
        cogs = table.find({"guildid":ctx.guild.id})
        for c in cogs:
            if cog.lower() not in c['activecogs'].lower():
                raise ModuleNotActivatedInGuild(f'{cog} not activated for {ctx.guild}')
            return True
    return commands.check(predicate)

def has_active_commands(command: str):
    async def predicate(ctx):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['prefixes']
        commands = table.find({"guildid":ctx.guild.id})
        for c in commands:
            if cog.lower() not in c['activecommands'].lower():
                raise CommandNotActivatedInGuild(f'{command} not activated for {ctx.guild}')
            return True
    return commands.check(predicate)

def is_guild(guildid):
    async def predicate(ctx):
        if ctx.guild.id != guildid:
            raise NotActivatedInGuild(f'not activated for {ctx.guild}')
        return True
    return commands.check(predicate)

def user_has_role():
    async def predicate(ctx):
        def gr(guild, command):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['hasrole']
            roleid = table.find({"guildid":guild.id, "command":{'$regex': f'{command.qualified_name}', '$options':'i'}})
            for role in roleid:
                return role['role']
            return None
        roleid = gr(ctx.guild, ctx.command)
        if roleid != None:
            role = ctx.guild.get_role(roleid)
            if role not in ctx.author.roles:
                raise missing_role(f'{ctx.author} missing role {role.name}')
            else:
                return True
        elif roleid == None:
            return True
    return commands.check(predicate)

def is_user_blacklisted():
    async def predicate(ctx):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['userfilter']
        users = table.find({"guild":ctx.guild.id, "user":ctx.author.id})
        for u in users:
            if u['user'] == ctx.author.id:
                raise UserInBlacklist(f'{ctx.author} has been blacklisted from using commands')
        return True
    return commands.check(predicate)
