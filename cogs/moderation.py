from datetime import datetime, timedelta
from typing import Optional
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Greedy, Converter, BadArgument
from discord.utils import find
from random import choice
import discord
import asyncio
from discord.ext import tasks, commands
from discord.ext.commands import bot_has_permissions
import time
from stuf import stuf
from dateutil.relativedelta import *
from customchecks import *
import random
import string
import re
from discord_slash import *
test_guilds = ['435038183231848449', '149167686159564800']

def random_string_generator():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    result=''
    for i in range(0, 8):
        result += random.choice(characters)
    return result

class Moderation(commands.Cog):
    """Moderation module"""

    def __init__(self, bot):
        self.bot = bot
        self.unmute_task.start()
        self.unban_task.start()

    @commands.command()
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @has_active_cogs("moderation")
    async def ban(self, ctx, user: discord.User = None, *, reason="No reason provided."):
        """lets me be ban users from the guild"""
        if user is None:
            embed = Embed(description=f":x: Please provide user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if user == ctx.message.author:
            embed = Embed(description=f":x: You can't ban yourself!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            member = ctx.guild.get_member(user.id)
            if user == member:
                if member.guild_permissions.administrator:
                    embed = Embed(description=f":x: {member.mention} is an Administartor! You can't ban Administrators!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if ctx.message.author.top_role.position == member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is the same rank as you! You can't ban people with the same rank as you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position < member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is higher rank than you! You can't ban people with higher rank than you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position > member.top_role.position:
                    cluster = Mongo.connect()
                    db = cluster["giffany"]
                    table = db['strikes']
                    while True:
                        sid = random_string_generator()
                        dbid = [i['strikeid'] for i in table.find({"strikeid":sid})]
                        if dbid == []:
                            break
                        for i in dbid:
                            if i == sid:
                                continue
                            else:
                                break

                    daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                    table.insert_one({"strikeid":str(sid), "guildid":int(ctx.guild.id), "user":int(member.id), "moderator":int(ctx.author.id), "action":str("Ban"), "reason":str(reason), "day":daytime})

                    await ctx.guild.ban(user=discord.Object(id=int(member.id)), reason=reason, delete_message_days=0)
                    embed = discord.Embed(description=f"{member} **was banned** | {reason} \n**User ID:** {member.id} \n**Actioned by:** {ctx.author.mention}",
                                          colour=0xF893B2,
                                          timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.send(embed=embed)
            else:
                cluster = Mongo.connect()
                db = cluster["giffany"]
                table = db['strikes']
                while True:
                    sid = random_string_generator()
                    dbid = [i['strikeid'] for i in table.find({"strikeid":sid})]
                    if dbid == []:
                        break
                    for i in dbid:
                        if i == sid:
                            continue
                        else:
                            break

                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                table.insert_one({"strikeid":str(sid), "guildid":int(ctx.guild.id), "user":int(user.id), "moderator":int(ctx.author.id), "action":str("Ban"), "reason":str(reason), "day":daytime})

                await ctx.guild.ban(discord.Object(id=int(user.id)), reason=reason, delete_message_days=0)
                embed = discord.Embed(description=f"{user} **was banned** | {reason} \n**User ID:** {user.id} \n**Actioned by:** {ctx.author.mention}",
                                      colour=0xF893B2,
                                      timestamp=datetime.utcnow())
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)
        else:
            embed = Embed(description=f":x: {user} is already banned",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

    @commands.command(aliases=['deleteban'])
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @has_active_cogs("moderation")
    async def dban(self, ctx, user: discord.User = None, nod:int=None, *, reason="No reason provided."):
        """lets me be ban users from the guild, and then I delete up to 7 days worth of their messages"""
        if user is None:
            embed = Embed(description=f":x: Please provide user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if user == ctx.message.author:
            embed = Embed(description=f":x: You can't ban yourself!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if nod == None:
            embed = Embed(description=f":x: Please provide number of days to delete messages, it can be upt o 7 days.",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if nod != 1 or 2 or 3 or 4 or 5 or 6 or 7:
            embed = Embed(description=f":x: Please provide correct number of days to delete messages, it can be upt o 7 days.",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            member = ctx.guild.get_member(user.id)
            if user == member:
                if member.guild_permissions.administrator:
                    embed = Embed(description=f":x: {member.mention} is an Administartor! You can't ban Administrators!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if ctx.message.author.top_role.position == member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is the same rank as you! You can't ban people with the same rank as you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position < member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is higher rank than you! You can't ban people with higher rank than you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position > member.top_role.position:
                    cluster = Mongo.connect()
                    db = cluster["giffany"]
                    table = db['strikes']
                    while True:
                        sid = random_string_generator()
                        dbid = [i['strikeid'] for i in table.find({"strikeid":sid})]
                        if dbid == []:
                            break
                        for i in dbid:
                            if i == sid:
                                continue
                            else:
                                break

                    daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                    table.insert_one({"strikeid":str(sid), "guildid":int(ctx.guild.id), "user":int(member.id), "moderator":int(ctx.author.id), "action":str("Ban"), "reason":str(reason), "day":daytime})

                    await ctx.guild.ban(user=discord.Object(id=int(member.id)), reason=reason, delete_message_days=int(nod))
                    embed = discord.Embed(description=f"{member} **was banned** | {reason} \n**User ID:** {member.id} \n**Actioned by:** {ctx.author.mention}\n {nod} days worth of messages deleted",
                                          colour=0xF893B2,
                                          timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.send(embed=embed)
            else:
                cluster = Mongo.connect()
                db = cluster["giffany"]
                table = db['strikes']
                while True:
                    sid = random_string_generator()
                    dbid = [i['strikeid'] for i in table.find({"strikeid":sid})]
                    if dbid == []:
                        break
                    for i in dbid:
                        if i == sid:
                            continue
                        else:
                            break

                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                table.insert_one({"strikeid":str(sid), "guildid":int(ctx.guild.id), "user":int(user.id), "moderator":int(ctx.author.id), "action":str("Ban"), "reason":str(reason), "day":daytime})

                await ctx.guild.ban(discord.Object(id=int(user.id)), reason=reason, delete_message_days=int(nod))
                embed = discord.Embed(description=f"{user} **was banned** | {reason} \n**User ID:** {user.id} \n**Actioned by:** {ctx.author.mention}\n {nod} days worth of messages deleted",
                                      colour=0xF893B2,
                                      timestamp=datetime.utcnow())
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)
        else:
            embed = Embed(description=f":x: {user} is already banned",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

    @commands.command(aliases=['tban'])
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @has_active_cogs("moderation")
    async def tempban(self, ctx, user:discord.User=None, time:int=None, type=None,*, reason="No reason provided."):
        """lets me temporarily ban users"""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tempbans']

        d = ['d', 'day', 'days']
        h = ['h', 'hour', 'hours']
        m = ['m', 'min', 'minute', 'minutes']
        w = ['w', 'week', 'weeks']

        if user == None:
            embed = Embed(description=f":x: Please provide a user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if user is ctx.author:
            embed = Embed(description=f":x: You can't ban yourself",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if time is None:
            embed = Embed(description=f":x: Please provide ban time",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if type is None:
            embed = Embed(description=f":x: Please provide ban time type. You can use: ['m', 'min', 'minute', 'minutes'], ['h', 'hour', 'hours'], ['d', 'day', 'days'], ['w', 'week', 'weeks'].",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            banned = table.find({"user":user.id, "guildid":ctx.guild.id})
            for u in banned:
                banned = u['user']
            if banned == user.id:
                db['tempbans'].delete_one({"guildid":ctx.guild.id, "user":user.id})

            if type.lower() in h:
                endtime = datetime.utcnow() + timedelta(hours=int(time))

            elif type.lower() in m:
                endtime = datetime.utcnow() + timedelta(minutes=int(time))

            elif type.lower() in d:
                endtime = datetime.utcnow() + timedelta(days=int(time))

            elif type.lower() in w:
                endtime = datetime.utcnow() + timedelta(weeks=int(time))

            elif type.lower() not in m or d or h:
                embed = Embed(description=f":x: Time type not supported. You can use: ['m', 'min', 'minute', 'minutes'], ['h', 'hour', 'hours'], ['d', 'day', 'days'], ['w', 'week', 'weeks'].",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

            member = ctx.guild.get_member(user.id)
            if user == member:
                if member.guild_permissions.administrator:
                    embed = Embed(description=f":x: {member.mention} is an Administartor! You can't ban Administrators!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if ctx.message.author.top_role.position == member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is the same rank as you! You can't ban people with the same rank as you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position < member.top_role.position:
                    embed = Embed(description=f":x: {member.mention} is higher rank than you! You can't ban people with higher rank than you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position > member.top_role.position:
                    while True:
                        sid = random_string_generator()
                        dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                        if dbid == []:
                            break
                        for i in dbid:
                            if i == sid:
                                continue
                            else:
                                break
                    daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                    db['strikes'].insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":ctx.author.id, "action":"Temp Ban", "day":daytime, "reason":reason})
                    table.insert_one({"guildid":ctx.guild.id, "user":member.id, "starttime":datetime.utcnow(), "endtime":endtime, "banreason":reason})

                    diff = relativedelta(endtime,  datetime.utcnow())
                    ends_in = f"{diff.years} Y {diff.months} M {diff.days} D {diff.hours} H {diff.minutes} min"

                    await ctx.guild.ban(discord.Object(id=int(member.id)), reason=reason, delete_message_days=0)
                    embed = discord.Embed(description=f"{member} **was temporarily banned** | {reason} \n**User ID:** {member.id} \n**Actioned by:** {ctx.author.mention}\nDuration: {ends_in}",
                                          colour=0xF893B2,
                                          timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=user.avatar_url)
                    await ctx.send(embed=embed)

            else:
                while True:
                    sid = random_string_generator()
                    dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                    if dbid == []:
                        break
                    for i in dbid:
                        if i == sid:
                            continue
                        else:
                            break
                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                db['strikes'].insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":user.id, "moderator":ctx.author.id, "action":"Temp Ban", "day":daytime, "reason":reason})
                table.insert_one({"guildid":ctx.guild.id, "user":user.id, "starttime":datetime.utcnow(), "endtime":endtime, "banreason":reason})

                diff = relativedelta(endtime,  datetime.utcnow())
                ends_in = f"{diff.years} Y {diff.months} M {diff.days} D {diff.hours} H {diff.minutes} min"

                await ctx.guild.ban(discord.Object(id=int(user.id)), reason=reason, delete_message_days=0)
                embed = discord.Embed(description=f"{user} **was temporarily banned** | {reason} \n**User ID:** {user.id} \n**Actioned by:** {ctx.author.mention}\nDuration: {ends_in}",
                                      colour=0xF893B2,
                                      timestamp=datetime.utcnow())
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)

        else:
            embed = Embed(description=f":x: {user} is already banned",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

    @tasks.loop(hours=1)
    async def unban_task(self):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tempbans']

        endtime = table.find({"endtime":{'$lte':f'{datetime.utcnow()}'}})
        for e in endtime:
            endtime = e['endtime']
            guildid = table.find({"endtime":e['endtime']})
            for g in guildid:
                guildid = g['guildid']
            userid = table.find({"endtime":e['endtime'], "guildid":guildid})
            for u in userid:
                userid = u['user']

            try:
                guild = await self.bot.fetch_guild(guildid)
            except discord.NotFound:
                print(f"[automod]|[unban_task]{guildid} not found in the guild list")
                table.delete_one({"user":userid, "endtime":e['endtime'], "guildid":guildid})
                return

            try:
                user = await self.bot.fetch_user(userid)
            except discord.NotFound:
                print(f"[automod]|[unban_task]{userid} not found")
                table.delete_one({"user":userid, "endtime":e['endtime'], "guildid":guildid})
                return

            try:
                await guild.fetch_ban(user)
            except discord.NotFound:
                print(f"[automod]|[unban_task]{user} not banned")
            else:
                await guild.unban(user, reason='ban time expired')

                while True:
                    sid = random_string_generator()
                    dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                    if dbid == []:
                        break
                    for i in dbid:
                        if i == sid:
                            continue
                        else:
                            break

                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                db['strikes'].insert_one({"strikeid":sid, "guildid":guild.id, "user":user.id, "moderator":'automod', "action":"Unban", "day":daytime, "reason":'ban time expired'})

                reason = table.find({"user":userid, "endtime":e['endtime'], "guildid":guildid})
                for r in reason:
                    banreason = r['banreason']

                logchannelid = db['logs'].find({"guild_id":guildid})
                for ch in logchannelid:
                    logchannelid = ch['channel_id']
                logchannel = await self.bot.fetch_channel(int(logchannelid))

                embed = discord.Embed(description=f"{user} **was unbanned by automod** | ban time expired \n**User ID:** {user.id} \n**Reason for ban:** {banreason}",
                                      colour=0xF893B2,
                                      timestamp=datetime.utcnow())
                embed.set_thumbnail(url=user.avatar_url)
                await logchannel.send(embed=embed)

                table.delete_one({"user":userid, "endtime":e['endtime'], "guildid":guildid})

    @commands.command()
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @has_active_cogs("moderation")
    async def unban(self, ctx, user:discord.User=None, *, reason="No reason provided."):
        """Unban member from guild. Use: .unban <member(s)> <reason>"""
        if user == None:
            embed = Embed(description=f":x: Please provide a user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if user == ctx.message.author:
            embed = Embed(description=f":x: This is not how that works buddy...",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            embed = Embed(description=f":x: {user} not banned",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        else:
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(description=f"{user} **was unbanned by {ctx.author.mention}** | {reason} \n**User ID:** {user.id}",
                                  colour=0xF893B2,
                                  timestamp=datetime.utcnow())
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

            cluster = Mongo.connect()
            db = cluster["giffany"]
            while True:
                sid = random_string_generator()
                dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == sid:
                        continue
                    else:
                        break
            author = ctx.message.author.id
            daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
            db['strikes'].insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":target.id, "moderator":str(author), "action":"Unban", "day":daytime, "reason":reason})

            tempbans = db['tempbans'].find({"guildid":ctx.guild.id, "user":user.id})
            for u in tempbans:
                if u['user'] == user.id:
                    db['tempbans'].delete_one({"guildid":ctx.guild.id, "user":user.id})

    @commands.command()
    @bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def kick(self, ctx, member: discord.Member=None, *, reason="No reason provided."):
        """lets me kick members from the guild"""
        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == ctx.message.author:
            embed = Embed(description=f":x: You can't kick yourself!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member.guild_permissions.administrator:
            embed = Embed(description=f":x: {member.mention} is an Administartor! You can't kick Administrators!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if ctx.message.author.top_role.position == member.top_role.position:
            embed = Embed(description=f":x: {member.mention} is the same rank as you! You can't kick people with the same rank as you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position < member.top_role.position:
            embed = Embed(description=f":x: {member.mention} is higher rank than you! You can't kick people with higher rank than you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position > member.top_role.position:
            await member.kick(reason=reason)
            embed = discord.Embed(description=f" {member.mention} **was kicked** for {reason} \n**Member ID:** {member.id} \n**Actioned by:** {ctx.author.mention}",
                                  colour=discord.Colour.from_rgb(119, 178, 85),
                                  timestamp=datetime.utcnow())
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)

            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['strikes']
            while True:
                sid = random_string_generator()
                dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == sid:
                        continue
                    else:
                        break
            author = ctx.message.author.id
            daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
            table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Kick", "day":daytime, "reason":reason})

    @commands.command(aliases=["purge", "clear", "clean", "remove"])
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("moderation")
    async def delete(self, ctx, amount=0):
        """Delete messages. Use: .delete <amount> Aliases:purge, clear, clean"""
        if amount == 0:
            embed = Embed(description=f":x: Please provide amount of messages to delete",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        async with ctx.typing():
            amount = amount + 1
            deleted = await ctx.channel.purge(limit=amount)
            await asyncio.sleep(1.2)

        embed = discord.Embed(description=f"Deleted {len(deleted)-1} messages",
                              colour=0xF893B2)
        await ctx.send(embed=embed)

    @commands.command(aliases=["udelete", "upurge", "uclear", "uclean", "uremove", "userpurge", "userclear", "userclean", "userremove"])
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("moderation")
    async def userdelete(self, ctx, user: discord.User=None, amount=300):
        """Delete all messages of an user."""
        msg = ''
        for g in ctx.guild.text_channels:
            msg = msg + f"{g.name}" + ","

        #print(msg.split(","))
        channels = [channel for channel in ctx.guild.text_channels if channel.name in msg.split(",")]
        #channel = [ctx.guild.get_channel(int(id_)) for id_ in msg.split(",") if len(id_)]

        if user == None:
            embed = Embed(description=f":x: Please provide a user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        elif amount == 0:
            embed = Embed(description=f":x: Please provide amount of messages to delete",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def check(msg):
            return msg.author.id == user.id

        await ctx.message.delete()
        for channel in channels:
            #print(channel)
            deleted = await channel.purge(limit=amount, check=check, before=None)
            if len(deleted) > 0:
                async with ctx.typing():
                    await asyncio.sleep(0.5)
                embed = discord.Embed(description=" Deleted {0} messages in {1} from {2}".format(len(deleted), channel.mention, user.mention),
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_footer(text=f"Auctioned by: {ctx.author}")
                await ctx.send(embed=embed)

    @commands.command()
    @bot_has_permissions(manage_roles=True)
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def mute(self, ctx, member: Member, time: int=None, type=None, *, reason="No reason provided."):
        """lets me temporarily mute members"""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['strikes']
        mutetable = db['mutes']
        muterole = discord.utils.get(ctx.guild.roles, name="Muted")
        member_roles = ",".join([str(role.id) for role in member.roles[1:]])
        def mutes(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            mutes = db['mutes'].find({"guildid":guild.id})
            for m in mutes:
                muted = m['user']
                return muted
            return None
        muted = mutes(ctx.guild)

        while True:
            sid = random_string_generator()
            dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
            if dbid == []:
                break
            for i in dbid:
                if i == sid:
                    continue
                else:
                    break

        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member is ctx.author:
            embed = Embed(description=f":x: You can't mute yourself",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if time is None:
            embed = Embed(description=f":x: Please provide mute time",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if type is None:
            embed = Embed(description=f":x: Please provide mute time type",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member.guild_permissions.administrator:
            embed = Embed(description=f":x: {member.mention} is an Administartor! You can't mute Administrators!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if ctx.message.author.top_role.position == member.top_role.position:
            embed = Embed(description=f":x: {member.mention} is the same rank as you! You can't mute people with the same rank as you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position < member.top_role.position:
            embed = Embed(description=f":x: {member.mention} is higher rank than you! You can't mute people with higher rank than you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position > member.top_role.position:
            d = ['d', 'day', 'days']
            h = ['h', 'hour', 'hours']
            m = ['m', 'min', 'minute', 'minutes']

        if type.lower() in d:
            if member.id == muted:
                oldendtime = mutetable.find({"guildid":ctx.guild.id, "user":member.id})
                for oet in oldendtime:
                    oldtime = oet['endtime']
                newtime = oldtime + timedelta(days=int(time))
                mutetable.update({"guildid":ctx.guild.id, "user":member.id}, {"$set":{"endtime":newtime}})
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more day(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(days=int(time))
                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                author = ctx.message.author.id
                table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Mute", "day":daytime, "reason":reason})
                mutetable.insert_one({"guildid":ctx.guild.id, "user":member.id, "roles":member_roles, "starttime":datetime.utcnow(), "endtime":endtime})
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} day(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() in h:
            if member.id == muted:
                oldendtime = mutetable.find({"guildid":ctx.guild.id, "user":member.id})
                for oet in oldendtime:
                    oldtime = oet['endtime']
                newtime = oldtime + timedelta(hours=int(time))
                mutetable.update({"guildid":ctx.guild.id, "user":member.id}, {"$set":{"endtime":newtime}})
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more hour(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(hours=int(time))
                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                author = ctx.message.author.id
                table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Mute", "day":daytime, "reason":reason})
                mutetable.insert_one({"guildid":ctx.guild.id, "user":member.id, "roles":member_roles, "starttime":datetime.utcnow(), "endtime":endtime})
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} hour(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() in m:
            if member.id == muted:
                oldendtime = mutetable.find({"guildid":ctx.guild.id, "user":member.id})
                for oet in oldendtime:
                    oldtime = oet['endtime']
                newtime = oldtime + timedelta(minutes=int(time))
                mutetable.update({"guildid":ctx.guild.id, "user":member.id}, {"$set":{"endtime":newtime}})
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more minute(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(minutes=int(time))
                daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                author = ctx.message.author.id
                table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Mute", "day":daytime, "reason":reason})
                mutetable.insert_one({"guildid":ctx.guild.id, "user":member.id, "roles":member_roles, "starttime":datetime.utcnow(), "endtime":endtime})
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} minute(s)",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() not in m or d or h:
            await ctx.message.delete()
            embed = Embed(description=f":x: Time type not supported. You can use: ['d', 'day', 'days'], ['h', 'hour', 'hours'], ['m', 'min', 'minute', 'minutes'].",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return



    @commands.command()
    @bot_has_permissions(manage_roles=True)
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def unmute(self, ctx, member: Member=None, *, reason: Optional[str] = "No reason provided."):
        """lets me unmute muted members"""
        if member is None:
            embed = Embed(description=f":x: Please provide a member",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['mutes']
        muterole = discord.utils.get(ctx.guild.roles, name="Muted")
        member_role_ids = [y.id for y in member.roles]
        userids = table.find({"guildid":ctx.guild.id, "user":member.id})
        for u in userids:
            uid = u['user']
            if (muterole.id in member_role_ids) and (member.id == uid):
                roleids = table.find({"guildid":ctx.guild.id, "user":member.id})
                for r in roleids:
                    rid = r['roles']
                roles = [ctx.guild.get_role(int(id_)) for id_ in rid.split(",") if len(id_)]

                await member.edit(roles=roles)
                embed = discord.Embed(title="Member was unmuted",
                                      description=member.mention + " was unmuted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention,
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

                table.delete_one({"guildid":ctx.guild.id, "user":member.id})
            else:
                embed = Embed(description=f":x: Member not muted",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

    @tasks.loop(minutes=1)
    async def unmute_task(self):
        db = await odm.connect()

        endtimes = await db.find(mutes, {'endtime':{'$lte':datetime.utcnow()}})
        for m in endtimes:
            try:
                guild = await self.bot.get_guild(m.guildid)
            except discord.NotFound:
                print(f"[automod]|[unmute_task]{m.guildid} not found in the guild list")
                entry_to_delete = await db.find(mutes, {'guildid':m.guildid, 'user':m.user, 'endtime':m.endtime})
                await db.delete(entry_to_delete)
                return

            try:
                member = await guild.get_member(m.user)
            except discord.NotFound:
                print(f"[automod]|[unmute_task]{m.user} not found in guild {guild}|{guild.id}")
                entry_to_delete = await db.find(mutes, {'guildid':m.guildid, 'user':m.user, 'endtime':m.endtime})
                await db.delete(entry_to_delete)
                return

            member = await guild.get_member(m.user)
            roles = [guild.get_role(int(id_)) for id_ in m.roles.split(",") if len(id_)]
            await = member.edit(roles=roles)

            lchs = await db.find(logs, {'guild_id':guild.id})
            for lch in lchs:
            try:
                logchannel = guild.get_channel(lch.channel_id)
            except discord.NotFound:
                print(f"[automod]|[unmute_task]{lch.channel_id} not found in guild {guild}|{guild.id}")
                entry_to_delete = await db.find(mutes, {'guildid':m.guildid, 'user':m.user, 'endtime':m.endtime})
                await db.delete(entry_to_delete)
                return

            embed = discord.Embed(description=f'{member.mention}|{member.id} **was unmuted** by **automod** | `Mute time expired`',
                                  colour=0xF893B2
                                  timestamp=datetime.utcnow())
            embed.set_thumbnail(url=member.avatar_url)
            await logchannel.send(embed=embed)
            entry_to_delete = await db.find(mutes, {'guildid':m.guildid, 'user':m.user, 'endtime':m.endtime})
            await db.delete(entry_to_delete)

    @commands.command(aliases=['modlogs'])
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def strikes(self, ctx, *, member: discord.User=None):
        """Lists all the strikes logged for the user."""
        if member == None:
            embed = Embed(description=f":x: Please provide a member",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def chunks(l, n):
            n = max(1, n)
            return (l[i:i+n] for i in range(0, len(l), n))

        def create_list(lst, n, s, e):
            lst = list(chunks(lst, n))
            for i in lst[s:e]:
                lst = i
            fl = ''
            for n in lst:
                fl = fl + n
            return fl

        def newpage(member, msg, sc, pages):
            embed = Embed(title=f"__Strikes for {member}({member.id})__ [{sc} found]",
                          description=msg,
                          colour=0xF893B2)
            embed.set_footer(text=pages)
            return embed

        def field(fld):
            field = ''
            for i in fld:
                field = field + f"\n{i},"

            return f

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        async def checkforuser(guild, userid):
            members = guild.members
            for m in members:
                if m.id == userid:
                    return m
                elif m.id != userid:
                    user = await self.bot.fetch_user(userid)
                    return f"{user}|{user.id}"
                else:
                    return f"Not found|{userid}"


        db = await odm.connect()

        msg = ''
        strike = await db.find(strikes, {"guildid":ctx.guild.id, "user":member.id})
        msg = [f"**Strike ID:** {s.strikeid} |**Reason:** {s.reason} |**Action**: {s.action} |**Moderator:** {s.moderator} |**Day:** {s.day} \n\n" for s in strike]
        strikecount = [str(s.strikeid)+"\n" for s in strike]
        sc = len(list(strikecount))

        if strikecount == []:
            embed = Embed(description=f"There are no strikes for {member}.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1
        nc = list(chunks(strikecount, 10))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
        await embedl.add_reaction('⬅️')
        await embedl.add_reaction('➡️')

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                await embedl.clear_reactions()
                break

            if (reaction.emoji == '➡️') and (counter < len(nc)):
                counter = counter + 1
                s = s + 1
                e = e + 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def warn(self, ctx, member: Member=None, *, reason="No reason provided."):
        """Lets me warn members."""
        if member == None:
            embed = Embed(description=f":x: Please provide a member",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        try:
            embed = Embed(description=f":grey_exclamation: **You have been warned in {ctx.guild} for:** {reason}",
                          colour=0xF893B2)
            await member.send(embed=embed)
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['strikes']
            while True:
                sid = random_string_generator()
                dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == sid:
                        continue
                    else:
                        break
            author = ctx.message.author.id
            daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
            table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Warn", "day":daytime, "reason":reason})
            embed = Embed(colour=0xF893B2,
                          timestamp=datetime.utcnow())
            embed.set_author(name=f"{member} warned | {reason}", icon_url=member.avatar_url)
            embed.set_footer(text=f'Member ID: {member.id}')
            await ctx.send(embed=embed)
        except:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['strikes']
            while True:
                sid = random_string_generator()
                dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == sid:
                        continue
                    else:
                        break
            author = ctx.message.author.id
            table.insert_one({"strikeid":sid, "guildid":ctx.guild.id, "user":member.id, "moderator":str(author), "action":"Warn", "day":datetime.utcnow(), "reason":reason})
            embed = Embed(colour=0xF893B2,
                          timestamp=datetime.utcnow())
            embed.set_author(name=f"Couldn't DM {member}, warn has been logged | {reason}", icon_url=member.avatar_url)
            embed.set_footer(text=f'Member ID: {member.id}')
            await ctx.send(embed=embed)

    @commands.command(aliases=['delwarn'])
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def warnremove(self, ctx, strikeid=None, *, reason='No reason provided'):
        if strikeid == None:
            embed = Embed(description=f":x: Please provide a strikeid",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = await odm.connect()
        table = strikes
        s = await db.find_one(table, {"guildid":ctx.guild.id, "strikeid":strikeid, 'action':'Warn'})
        if s.strikeid == strikeid:
            embed = discord.Embed(title=f'Strike removed by {ctx.author}|{ctx.author.id} | {reason}',
                                  description=f"**Strike ID:** {s.strikeid} |**Reason:** {s.reason} |**Action**: {s.action} |**Moderator:** {s.moderator} |**Day:** {s.day}",
                                  colour=0xF893B2,
                                  timestamp=datetime.utcnow())
            await ctx.send(embed=embed)
            await db.delete(s)
        else:
            embed = Embed(description=f":x: Warn with strike ID `{strikeid}` not found",
                          color=0xDD2222)
            await ctx.send(embed=embed)

    @commands.command(aliases=['warns'])
    @commands.has_permissions(kick_members=True)
    @has_active_cogs("moderation")
    async def warnings(self, ctx, *, member: discord.User=None):
        """Lists all the warns logged for the user."""
        if member == None:
            embed = Embed(description=f":x: Please provide a member",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def chunks(l, n):
            n = max(1, n)
            return (l[i:i+n] for i in range(0, len(l), n))

        def create_list(lst, n, s, e):
            lst = list(chunks(lst, n))
            for i in lst[s:e]:
                lst = i
            fl = ''
            for n in lst:
                fl = fl + n
            return fl

        def newpage(member, msg, sc, pages):
            embed = Embed(title=f"__Warnings for {member}({member.id})__ [{sc} found]",
                          description=msg,
                          colour=0xF893B2)
            embed.set_footer(text=pages)
            return embed

        def field(fld):
            field = ''
            for i in fld:
                field = field + f"\n{i},"

            return f

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        async def checkforuser(guild, userid):
            members = guild.members
            for m in members:
                if m.id == userid:
                    return m
                elif m.id != userid:
                    user = await self.bot.fetch_user(userid)
                    return f"{user}|{user.id}"
                else:
                    return f"Not found|{userid}"


        db = await odm.connect()
        table = strikes

        msg = ''
        strikeids = await db.find(table, {"guildid":ctx.guild.id, "user":member.id, "action":"Warn"})
        for s in strikeids:
            sid = s.strikeid
            reasons = await db.find(table, {"guildid":ctx.guild.id, "user":member.id, "strikeid":s.strikeid})

            moderators = await db.find(table, {"guildid":ctx.guild.id, "user":member.id, "strikeid":s.strikeid})

            days = await db.find(table, {"guildid":ctx.guild.id, "user":member.id, "strikeid":s.strikeid})
            for r in reasons:
                reason = r.reason
            for m in moderators:
                mods = await checkforuser(ctx.guild, m.moderator)
            for d in days:
                day = d.day
                msg = msg + f"**Strike ID:** {sid} |**Reason:** {reason} |**Moderator:** {mods} |**Day:** {day} \n\n ,"
        msg = msg.split(',')

        strikecount = [str(s.strikeid)+"\n" for s in strikeids]
        sc = len(list(strikecount))


        if strikecount == []:
            embed = Embed(description=f"There are no warnings for {member}.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1
        nc = list(chunks(strikecount, 10))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
        await embedl.add_reaction('⬅️')
        await embedl.add_reaction('➡️')

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                await embedl.clear_reactions()
                break

            if (reaction.emoji == '➡️') and (counter < len(nc)):
                counter = counter + 1
                s = s + 1
                e = e + 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(member, create_list(msg, 10, s, e), sc, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('moderation module loaded')
