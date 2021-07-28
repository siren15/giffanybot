import discord
import asyncio
from discord import Member, Embed
from datetime import datetime, timedelta, time
from random import choice, randint, choices
from discord.ext import commands, tasks
from string import Template
from stuf import stuf
from customchecks import *
from discord.utils import get
import random
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import re

def random_string_generator():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    result=''
    for i in range(0, 8):
        result += random.choice(characters)
    return result

class Giveaways(commands.Cog):
    """Giveaways"""
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_task.start()
        self.giveaway_count_task.start()

    @commands.command(aliases=['gcreate'])
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs('giveaways')
    async def giveawaycreate(self, ctx):
        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author == ctx.message.author

        embed = discord.Embed(
            description=f":tada: Alright! Let's set up your giveaway! First, what channel do you want the giveaway in? Please type the name of a channel in this server, or type `abort` to abort the process.",
            colour=0xF893B2)
        start_embed = await ctx.send(embed=embed)

        ischannel = False
        while ischannel == False:
            try:
                giveaway_channel = await self.bot.wait_for('message', timeout=120, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    await start_embed.delete()
                    await ctx.message.delete()

            gch = giveaway_channel.content
            lowgch = gch.lower()

            if lowgch == "abort":
                embed = Embed(
                    description=":x: Creation process aborted",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await start_embed.delete()
                await giveaway_channel.delete()
                await ctx.message.delete()
                return

            else:
                if giveaway_channel.content.startswith('<#') and giveaway_channel.content.endswith('>'):
                    gid = giveaway_channel.content.replace('<#', '')
                    id = gid.replace('>', '')
                    gch = id
                else:
                    gch = giveaway_channel.content

                if gch.isnumeric() == True:
                    channel = await self.bot.fetch_channel(int(gch))
                else:
                    channel = get(ctx.guild.channels, name=gch)

                if channel != None:
                    ischannel = True

                elif channel == None:
                    embed = Embed(
                        description=f":x: `{gch}` not found. Try again.",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    await giveaway_channel.delete()

        embed = Embed(description=f":tada: Sweet! The giveaway will be in {channel.mention}! Next, how long should the giveaway last? \nPlease enter the duration of the giveaway. For minutes use include M at the end, for hours include H at the end for seconds include S at the end, and for days use D at the end. \nOr type `abort` to abort the process.\n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                      colour=0xF893B2)
        time_embed = await ctx.send(embed=embed)
        istime = False
        while istime == False:
            try:
                time = await self.bot.wait_for('message', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await start_embed.delete()
                    await giveaway_channel.delete()
                    await time_embed.delete()
                    await ctx.message.delete()

            tc = time.content
            lowtc = tc.lower()

            if lowtc == "abort":
                embed = Embed(
                    description=":x: Creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await start_embed.delete()
                await giveaway_channel.delete()
                await time_embed.delete()
                await ctx.message.delete()
                return
            else:
                tnum = [int(i) for i in lowtc.split() if i.isdigit()]
                if tnum == []:
                    embed = Embed(description=f":x: Time formatting not correct. Try again. \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    await time.delete()

                else:
                    for tnum in tnum:
                        tnum = tnum
                        ttype = [str(type) for type in lowtc.split() if not type.isdigit()]
                        for ttype in ttype:
                            ttype = ttype

                if ttype not in ['s', 'm', 'h', 'd']:
                    embed = Embed(description=f":x: Time type not supported. Try again. \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    await time.delete()

                if 's' in ttype:
                    t = lowtc.replace('s', '')
                    if (int(t) > 1209600) or (int(t) < 10):
                        embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        await time.delete()
                    else:
                        endtime = datetime.utcnow() + timedelta(seconds=int(t))
                        endtime_type = 's'
                if 'm' in ttype:
                    t = lowtc.replace('m', '')
                    if (int(t) > 20160) or (int(t) < 0.17):
                        embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        await time.delete()
                    else:
                        endtime = datetime.utcnow() + timedelta(minutes=int(t))
                        endtime_type = 'm'
                if 'h' in ttype:
                    t = lowtc.replace('h', '')
                    if (int(t) > 336) or (int(t) < 0.002777778):
                        embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        await time.delete()
                    else:
                        endtime = datetime.utcnow() + timedelta(hours=int(t))
                        endtime_type = 'h'
                if 'd' in ttype:
                    t = lowtc.replace('d', '')
                    if (int(t) > 14) or (int(t) < 0.00011574075):
                        embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        await time.delete()
                    else:
                        endtime = datetime.utcnow() + timedelta(days=int(t))
                        endtime_type = 'd'

                ends_in_sec = (endtime - datetime.utcnow()).seconds
                ends_in = timedelta(seconds = ends_in_sec)
                istime = True

        embed = Embed(description=f":tada: Neat! This giveaway will last {ends_in}! Now, how many winners should there be? \nPlease enter a number of winners between 1 and 20. \nOr type `abort` to abort the process.",
                      colour=0xF893B2)
        winners_embed = await ctx.send(embed=embed)

        iswinner = False
        while iswinner == False:
            try:
                winners = await self.bot.wait_for('message', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await start_embed.delete()
                    await giveaway_channel.delete()
                    await time_embed.delete()
                    await winners_embed.delete()
                    await ctx.message.delete()

            wc = winners.content
            lowwc = wc.lower()

            if lowwc == "abort":
                embed = Embed(
                    description=":x: Creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await start_embed.delete()
                await giveaway_channel.delete()
                await time_embed.delete()
                await winners_embed.delete()
                await winners.delete()
                await ctx.message.delete()
                return
            else:
                if winners.content.isdigit() == True:
                    if (int(winners.content) > 20) or (int(winners.content) < 1):
                        embed = Embed(
                            description=":x: Please enter a number of winners between 1 and 20. Try again.",
                            color=0xDD2222)
                        await ctx.channel.send(embed=embed)
                        await winners.delete()
                    else:
                        winnersnum = winners.content
                        iswinner = True
                else:
                    embed = Embed(
                        description=":x: Please enter a number of winners between 1 and 20. Try again.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await winners.delete()

        embed = Embed(description=f":tada: Ok! {winnersnum} winner(s) it is! \nNow type role requirement for this giveaway, or type `None` to not have one. \nOr type `abort` to abort the process.",
                      colour=0xF893B2)
        req_embed = await ctx.send(embed=embed)

        isreq = False
        while isreq == False:
            try:
                req = await self.bot.wait_for('message', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await start_embed.delete()
                    await giveaway_channel.delete()
                    await time_embed.delete()
                    await winners_embed.delete()
                    await ctx.message.delete()

            rq = req.content
            lowrq = rq.lower()

            if lowrq == "abort":
                embed = Embed(
                    description=":x: Creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await start_embed.delete()
                await giveaway_channel.delete()
                await time_embed.delete()
                await winners_embed.delete()
                await winners.delete()
                await req_embed.delete()
                await req.delete()
                await ctx.message.delete()
                return
            else:
                if lowrq == "none":
                    rolereq = None
                    isreq = True
                else:
                    if req.content.startswith('<@') and req.content.endswith('>'):
                        reqid = giveaway_channel.content.replace('<@', '')
                        id = reqid.replace('>', '')
                        role = id
                    else:
                        role = req.content

                    if role.isnumeric() == True:
                        rolereq = ctx.guild.get_role(int(role))
                        rq = rolereq
                        rolereq=rolereq.id
                        isreq = True
                    else:
                        rolereq = get(ctx.guild.roles, name=role)
                        rq = rolereq
                        rolereq=rolereq.id
                        isreq = True

                    if rolereq != None:
                        rq = rq.mention
                    else:
                        rq = None

                    if rolereq == []:
                        embed = Embed(
                            description=":x: Couln't find that role, try again.",
                            color=0xDD2222)
                        await ctx.channel.send(embed=embed)
                        await req.delete()

        embed = Embed(description=f":tada: Ok! {rq} it is! Finally, what do you want to give away? Please enter the giveaway prize. This will also begin the giveaway.\nOr type `abort` to abort the process.",
                      colour=0xF893B2)
        prize_embed = await ctx.send(embed=embed)

        try:
            prize = await self.bot.wait_for('message', timeout=60.0, check=check)

        except asyncio.TimeoutError:
                embed = Embed(
                    description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, creation cancelled.",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await start_embed.delete()
                await giveaway_channel.delete()
                await time_embed.delete()
                await winners_embed.delete()
                await ctx.message.delete()

        pr = prize.content
        lowpr = pr.lower()

        if lowpr == "abort":
            embed = Embed(
                description=":x: Creation process aborted",
                color=0xDD2222)
            await ctx.channel.send(embed=embed)
            await start_embed.delete()
            await giveaway_channel.delete()
            await time_embed.delete()
            await winners_embed.delete()
            await winners.delete()
            await req_embed.delete()
            await req.delete()
            await prize_embed.delete()
            await prize.delete()
            await ctx.message.delete()
            return
        else:
            embed = Embed(title=f"🎉Giveaway started!🎉 \nFor: {prize.content}",
                          description=f"React with :tada: to enter!\nNumber of winners: {winnersnum}\nRole requirement: {rq}\nHosted by: {ctx.author.mention}",
                          colour=0xF893B2,
                          timestamp=datetime.utcnow())
            embed.set_footer(text=f"Ends in: {ends_in}[Last Update: {datetime.utcnow().strftime('%H:%M:%S')}]|Started")
            m = await channel.send(embed=embed)
            await m.add_reaction('🎉')

            if endtime_type == 's':
                t = lowtc.replace('s', '')
                endtime = datetime.utcnow() + timedelta(seconds=int(t))
            if endtime_type == 'm':
                t = lowtc.replace('m', '')
                endtime = datetime.utcnow() + timedelta(minutes=int(t))
            if endtime_type == 'h':
                t = lowtc.replace('h', '')
                endtime = datetime.utcnow() + timedelta(hours=int(t))
            if endtime_type == 'd':
                t = lowtc.replace('d', '')
                endtime = datetime.utcnow() + timedelta(days=int(t))

            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db["giveaways"]

            while True:
                gid = random_string_generator()
                dbid = [i['giveawaynum'] for i in table.find({"giveawaynum":gid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == gid:
                        continue
                    else:
                        break

            table.insert_one({"giveawaynum":gid, "guildid":ctx.guild.id, "authorid":ctx.author.id, "starttime":datetime.utcnow(), "endtime":endtime, "giveawaychannelid":channel.id, "giveawaymessageid":m.id, "reqrid":rolereq, "winnersnum":winnersnum, "prize":prize.content})

            embed = Embed(description=f"🎉Giveaway for {prize.content} in {channel.mention} started!🎉",
                          colour=0xF893B2)
            await ctx.send(embed=embed)

    @commands.command(aliases=['gstart'])
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs('giveaways')
    async def giveawaystart(self, ctx, time: int=None, type: str=None, winnersnum: int=None, *, prize: str=None):
        """Start a giveaway. Alias: .gstart"""
        def endsin(sec):
           sec = sec % (24 * 3600)
           hour = sec // 3600
           sec %= 3600
           min = sec // 60
           sec %= 60
           return "%02d:%02d:%02d" % (hour, min, sec)

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['giveaways']

        while True:
            gid = random_string_generator()
            dbid = [i['giveawaynum'] for i in table.find({"giveawaynum":gid})]
            if dbid == []:
                break
            for i in dbid:
                if i == gid:
                    continue
                else:
                    break

        if time is None:
            await ctx.message.delete()
            embed = Embed(description=f":x: Please provide time",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if type is None:
            await ctx.message.delete()
            embed = Embed(description=f":x: Please provide time type",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        s = ['s', 'second', 'seconds']
        m = ['m', 'min', 'minute', 'minutes']
        h = ['h', 'hour', 'hours']
        d = ['d', 'day', 'days']
        t = time
        type = type.lower()

        if time.isdigit() == False:
            embed = Embed(description=f":x: Time formatting not correct. Try again. \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if type not in s or m or h or d:
            embed = Embed(description=f":x: Time type not supported. Try again. \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if type in s:
            if (int(t) > 1209600) or (int(t) < 10):
                embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                              color=0xDD2222)
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(seconds=int(t))
        if type in m:
            if (int(t) > 20160) or (int(t) < 0.17):
                embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                await time.delete()
            else:
                endtime = datetime.utcnow() + timedelta(minutes=int(t))
                endtime_type = 'm'
        if type in h:
            if (int(t) > 336) or (int(t) < 0.002777778):
                embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                await time.delete()
            else:
                endtime = datetime.utcnow() + timedelta(hours=int(t))
                endtime_type = 'h'
        if type in d:
            if (int(t) > 14) or (int(t) < 0.00011574075):
                embed = Embed(description=f":x: Oh! Sorry! Giveaway time must not be shorter than 10 seconds and no longer than 2 weeks Mind trying again? \n\n[Examples: `10 S`, `10 M`, `10 H`, `10 D`]",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                await time.delete()
            else:
                endtime = datetime.utcnow() + timedelta(days=int(t))
                endtime_type = 'd'

        ends_in_sec = (endtime - datetime.utcnow()).seconds
        ends_in = timedelta(seconds = ends_in_sec)

        embed = Embed(title=f"🎉Giveaway started!🎉 \nFor: {prize}",
                      description=f"React with :tada: to enter!\nNumber of winners: {int(winners)}\nHosted by: {ctx.author.mention}",
                      colour=0xF893B2,
                      timestamp=datetime.utcnow())
        embed.set_footer(text=f"Ends in: {ends_in}[Last Update: {datetime.utcnow().strftime('%H:%M:%S')}]|Started")
        m = await ctx.send(embed=embed)
        await m.add_reaction('🎉')

        table.insert_one({"giveawaynum":gid, "guildid":ctx.guild.id, "authorid":ctx.author.id, "endtime":endtime, "giveawaychannelid":m.channel.id, "giveawaymessageid":m.id, "winnersnum":winnersnum, "prize":prize})


    @tasks.loop(minutes=10)
    async def giveaway_count_task(self):
        def endsin(sec):
           sec = sec % (24 * 3600)
           hour = sec // 3600
           sec %= 3600
           min = sec // 60
           sec %= 60
           return "%02d:%02d:%02d" % (hour, min, sec)

        def guild_id(endtime):
            cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
            db = cluster["giffany"]
            results = db['giveaways'].find({"endtime":endtime})
            for r in results:
                return r['guildid']

        def field(item, endtime, guildid):
            cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
            db = cluster["giffany"]
            results = db['giveaways'].find({"endtime":endtime, "guildid":guildid})
            for r in results:
                return r[f'{item}']
            return None

        cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
        db = cluster["giffany"]
        table = db['giveaways']
        endtime = table.find({"endtime":{'$gt':datetime.utcnow()}})
        for e in endtime:
            guildid = guild_id(e["endtime"])
            giveawaychannelid = field('giveawaychannelid', e["endtime"], guildid)
            giveawaymessageid = field('giveawaymessageid', e["endtime"], guildid)
            prize = field('prize', e["endtime"], guildid)
            reqrid = field('reqrid', e["endtime"], guildid)
            authorid = field('authorid', e["endtime"], guildid)
            winnersnum = field('winnersnum', e["endtime"], guildid)
            end_time = field('endtime', e["endtime"], guildid)
            start_time = field('starttime', e["endtime"], guildid)

            ends_in_sec = (end_time - datetime.utcnow()).seconds
            ends_in = endsin(int(ends_in_sec))

            for guild in self.bot.guilds:
                if guild.id == guildid:
                    author = [member for member in guild.members if member.id == authorid]
                    for author in author:
                        author = author

                    if reqrid == None:
                        rolereq=None
                    else:
                        rolereq = guild.get_role(int(reqrid))
                        rolereq = rolereq.mention
                    giveaway_channel = await self.bot.fetch_channel(int(giveawaychannelid))
                    giveaway_message = await giveaway_channel.fetch_message(giveawaymessageid)
                    embed=Embed()
                    embed = Embed(title=f"🎉Giveaway started!🎉 \nFor: {prize}",
                                  description=f"React with :tada: to enter!\nNumber of winners: {winnersnum}\nRole requirement: {rolereq}\nHosted by: {author.mention}",
                                  colour=0xF893B2,
                                  timestamp=start_time)
                    embed.set_footer(text=f"Ends in: {ends_in}[Last Update: {datetime.utcnow().strftime('%H:%M:%S')}]|Started")
                    await giveaway_message.edit(embed=embed)

    @tasks.loop(seconds=10)
    async def giveaway_task(self):
        def guild_id(endtime):
            cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
            db = cluster["giffany"]
            results = db['giveaways'].find({"endtime":endtime})
            for r in results:
                return r['guildid']

        def field(item, endtime, guildid):
            cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
            db = cluster["giffany"]
            results = db['giveaways'].find({"endtime":endtime, "guildid":guildid})
            for r in results:
                return r[f'{item}']
            return None

        cluster = MongoClient("mongodb+srv://zep:6hEIdCzAQKh6U59S@journal-1.nrq1q.mongodb.net/zephyrus?retryWrites=true&w=majority")
        db = cluster["giffany"]
        table = db['giveaways']
        endtime = table.find({"endtime":{'$lte':datetime.utcnow()}})
        for e in endtime:
            guildid = guild_id(e["endtime"])
            giveawaychannelid = field('giveawaychannelid', e["endtime"], guildid)
            giveawaymessageid = field('giveawaymessageid', e["endtime"], guildid)
            gid = field('giveawaynum', e["endtime"], guildid)
            prize = field('prize', e["endtime"], guildid)
            authorid = field('authorid', e["endtime"], guildid)
            winnersnum = field('winnersnum', e["endtime"], guildid)
            reqrid = db['giveaways'].find({"endtime":e["endtime"], "guildid":guildid})
            req = field('reqrid', endtime=e["endtime"], guildid=guildid)

            for guild in self.bot.guilds:
                if guild.id == guildid:
                        giveaway_channel = await self.bot.fetch_channel(int(giveawaychannelid))
                        giveaway_message = await giveaway_channel.fetch_message(int(giveawaymessageid))

                        for reaction in giveaway_message.reactions:
                            if reaction.emoji == '🎉':
                                users = await reaction.users().flatten()
                                users = [u.id for u in users if not u.bot]
                                member_pool_all = [member for member in guild.members if member.id in users]
                                #req_roles = [reqrid.reqrid for reqrid in reqrid]
                                author = [member for member in guild.members if member.id == authorid]
                                for author in author:
                                    author = author.mention
                                if req is None:
                                    member_pool = [member.id for member in guild.members if member.id in users]
                                    try:
                                        winners = choices(member_pool, k=int(winnersnum))
                                    except IndexError:
                                        embed = Embed(title=f"🎉Giveaway ended!🎉 \nFor: {prize}",
                                                      description=f"Not enough participants. \nHosted by: {author}",
                                                      colour=0xF893B2)
                                        embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                                        await giveaway_message.edit(embed=embed)
                                        table.delete_one({"endtime":e["endtime"], "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                        #db.commit()
                                        return
                                    winner = [member.mention for member in guild.members if member.id in winners]
                                    for win in winner:
                                        win = win
                                    embed = Embed(title=f"🎉Giveaway ended!🎉 \nFor: {prize}",
                                                  description=f"Winner: {winner}\nHosted by: {author}",
                                                  colour=0xF893B2)
                                    embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                                    await giveaway_message.edit(embed=embed)
                                    await giveaway_message.channel.send(f"🎉Congrats {win}!!🎉 You won **{prize}**!")
                                    table.delete_one({"endtime":e["endtime"], "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                    #db.commit()
                                else:
                                    rrq = guild.get_role(int(req))
                                    member_pool = [member.id for member in member_pool_all if rrq in member.roles]
                                    try:
                                        winners = choices(member_pool, k=int(winnersnum))
                                    except IndexError:
                                        embed = Embed(title=f"🎉Giveaway ended!🎉 \nFor: {prize}",
                                                      description=f"Not enough participants. \nHosted by: {author}",
                                                      colour=0xF893B2)
                                        embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                                        await giveaway_message.edit(embed=embed)
                                        table.delete_one({"endtime":e["endtime"], "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                        #db.commit()
                                        return

                                    winner = [member.mention for member in guild.members if member.id in winners]
                                    for win in winner:
                                        win = win

                                    embed = Embed(title=f"🎉Giveaway ended!🎉 \nFor: {prize}",
                                                  description=f"Winner(s): {winner}\nHosted by: {author}",
                                                  colour=0xF893B2)
                                    embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                                    await giveaway_message.edit(embed=embed)
                                    await giveaway_message.channel.send(f"🎉Congrats {win}!!🎉 You won **{prize}**!")
                                    table.delete_one({"endtime":e["endtime"], "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                    #db.commit()

def setup(bot):
    bot.add_cog(Giveaways(bot))
    print('giveaway module loaded')
