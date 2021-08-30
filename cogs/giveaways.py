import discord
import asyncio
from discord import Member, Embed
from datetime import datetime, timedelta, time
from random import choice, randint, choices
from discord.ext import commands, tasks
from string import Template
from customchecks import *
from discord.utils import get
import random
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from dateutil.relativedelta import *
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

                diff = relativedelta(endtime,  datetime.utcnow())
                ends_in = f"{diff.days} D, {diff.hours} H, {diff.minutes} M, {diff.seconds} S"
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

            table.insert_one({"giveawaynum":gid, "guildid":ctx.guild.id, "authorid":ctx.author.id, "starttime":datetime.utcnow(), "endtime":endtime, "giveawaychannelid":channel.id, "giveawaymessageid":m.id, "reqrid":rolereq, "winnersnum":winnersnum, "prize":prize.content, "status":"Active"})

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

        diff = relativedelta(endtime,  datetime.utcnow())
        ends_in = f"{diff.days} D, {diff.hours} H, {diff.minutes} M, {diff.seconds} S"

        embed = Embed(title=f"🎉Giveaway started!🎉 \nFor: {prize}",
                      description=f"React with :tada: to enter!\nNumber of winners: {int(winners)}\nHosted by: {ctx.author.mention}",
                      colour=0xF893B2,
                      timestamp=datetime.utcnow())
        embed.set_footer(text=f"Ends in: {ends_in}[Last Update: {datetime.utcnow().strftime('%H:%M:%S')}]|Started")
        m = await ctx.send(embed=embed)
        await m.add_reaction('🎉')

        table.insert_one({"giveawaynum":gid, "guildid":ctx.guild.id, "authorid":ctx.author.id, "endtime":endtime, "giveawaychannelid":m.channel.id, "giveawaymessageid":m.id, "winnersnum":winnersnum, "prize":prize, "status":"Active"})

    @commands.command(aliases=['glist', 'giveawayslist', 'giveawaylist'])
    @commands.has_permissions(administrator=True)
    async def giveaways(self, ctx):
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

        def newpage(guild, active, ended, sc, pages):
            embed = Embed(title=f"__Giveaways for {guild}__ [{sc} found]",
                          colour=0xF893B2)
            embed.add_field(name="Active:", value=active)
            embed.add_field(name="Ended:", value=ended)
            embed.set_footer(text=pages)
            return embed

        def field(fld):
            field = ''
            for i in fld:
                field = field + f"\n{i},"

            return f

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        db = odm.connect()
        table = giveaways

        active = await db.find(table, {"guildid":ctx.guild.id, "status":"Active"})
        active = [str(name['name'])+"\n" for name in names]

        ended = await db.find(table, {"guildid":ctx.guild.id, "status":"Ended"})
        ended = [str(name['rolename'])+"\n" for name in roles]

        if names == []:
            embed = Embed(description=f"There are no giveyous for {ctx.guild}.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1
        nc = list(chunks(names, 10))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(create_list(names, 10, s, e), create_list(roles, 10, s, e), ctx.guild, footer))
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
                await embedl.edit(embed=newpage(create_list(names, 10, s, e), create_list(roles, 10, s, e), ctx.guild, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(create_list(names, 10, s, e), create_list(roles, 10, s, e), ctx.guild, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reroll(self, ctx, gid=None):
        if gid == None:
            embed = Embed(description=f":x: Please enter giveaway message id",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        db = await odm.connect()
        ge = await db.find(giveaways, giveaways.giveawaymessageid==gid)
        for ge in ge:
            print(ge)
            if (ge.giveawaymessageid == gid) and (ge.guildid == ctx.guild.id):
                giveaway_channel = await ctx.guild.get_channel(int(ge.giveawaychannelid))
                giveaway_message = await giveaway_channel.fetch_message(int(ge.giveawaymessageid))
                req = ge.reqrid
                winnersnum = ge.winnersnum
                guild=ctx.guild
            
            for reaction in giveaway_message.reactions:
                if reaction.emoji == '🎉':
                    users = await reaction.users().flatten()
                    users = [u.id for u in users if not u.bot]
                    member_pool_all = [member for member in guild.members if member.id in users]
                    author = [member for member in guild.members if member.id == ge.authorid]
                    for author in author:
                        author = author.mention
                    if req is None:
                        member_pool = [member.id for member in guild.members if member.id in users]
                        try:
                            winners = choices(member_pool, k=int(winnersnum))
                        except IndexError:
                            embed = Embed(title=f"🎉Giveaway ended[reroll]!🎉 \nFor: {ge.prize}",
                                        description=f"Not enough participants. \nHosted by: {author}",
                                        colour=0xF893B2)
                            embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                            await giveaway_message.edit(embed=embed)
                            return

                        winner = [member.mention for member in guild.members if member.id in winners]
                        for win in winner:
                            win = win
                        embed = Embed(title=f"🎉Giveaway ended[reroll]!🎉 \nFor: {ge.prize}",
                                    description=f"Winner: {winner}\nHosted by: {author}",
                                    colour=0xF893B2)
                        embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                        await giveaway_message.edit(embed=embed)
                        await giveaway_message.channel.send(f"🎉Congrats {win}!!🎉 You won **{ge.prize}**!")
                        return
                            
                    else:
                        rrq = guild.get_role(int(req))
                        member_pool = [member.id for member in member_pool_all if rrq in member.roles]
                        try:
                            winners = choices(member_pool, k=int(winnersnum))
                        except IndexError:
                            embed = Embed(title=f"🎉Giveaway ended[reroll]!🎉 \nFor: {ge.prize}",
                                        description=f"Not enough participants. \nHosted by: {author}",
                                        colour=0xF893B2)
                            embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                            await giveaway_message.edit(embed=embed)
                            return

                        winner = [member.mention for member in guild.members if member.id in winners]
                        for win in winner:
                            win = win

                        embed = Embed(title=f"🎉Giveaway ended[reroll]!🎉 \nFor: {ge.prize}",
                                    description=f"Winner(s): {winner}\nHosted by: {author}",
                                    colour=0xF893B2)
                        embed.set_footer(text=f"Ended at: {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}")
                        await giveaway_message.edit(embed=embed)
                        await giveaway_message.channel.send(f"🎉Congrats {win}!!🎉 You won **{ge.prize}**!")
                        return
            


    @tasks.loop(minutes=1)
    async def giveaway_count_task(self):
        async def guild_id(endtime):
            db = await odm.connect()
            results = await db.find(giveaways, {"status":"Active", "endtime":endtime})
            for r in results:
                return r.guildid

        db = await odm.connect()
        table = giveaways
        endtime = await db.find(table, {"status":"Active", "endtime":{'$gt':datetime.utcnow()}})
        for e in endtime:
            guildid = await guild_id(e.endtime)

            search = await db.find(table, {"status":"Active", "endtime":e.endtime, "guildid":guildid})
            for s in search:
                giveawaychannelid = s.giveawaychannelid
                giveawaymessageid = s.giveawaymessageid
                prize = s.prize
                reqrid = s.reqrid
                authorid = s.authorid
                winnersnum = s.winnersnum
                end_time = s.endtime
                start_time = s.starttime

                diff = relativedelta(s.endtime,  datetime.utcnow())
                ends_in = f"{diff.days} D, {diff.hours} H, {diff.minutes} M, {diff.seconds} S"

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
                        embed.set_footer(text=f"Ends in: {ends_in}")
                        await giveaway_message.edit(embed=embed)

    @tasks.loop(minutes=10)
    async def giveaway_task(self):
        async def guild_id(endtime):
            db = await odm.connect()
            table = giveaways
            results = await db.find(table, {"status":"Active", "endtime":endtime})
            for r in results:
                return r.guildid

        db = await odm.connect()
        table = giveaways
        endtime = await db.find(table, {"status":"Active", "endtime":{'$lte':datetime.utcnow()}})
        for e in endtime:
            guildid = await guild_id(e.endtime)

            search = await db.find(table, {"status":"Active", "endtime":e.endtime, "guildid":guildid})
            for s in search:
                giveawaychannelid = s.giveawaychannelid
                giveawaymessageid = s.giveawaymessageid
                prize = s.prize
                reqrid = s.reqrid
                authorid = s.authorid
                winnersnum = s.winnersnum
                end_time = s.endtime
                start_time = s.starttime
                gid = s.giveawaynum
                req = s.reqrid

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
                                            giveaway_entry = await db.find(table, {"status":"Active", "endtime":e.endtime, "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                            for ge in giveaway_entry:
                                                if (ge.guildid == guild.id) and (ge.giveawaynum == gid):
                                                    if ge.status == "Active":
                                                        ge.status = "Ended"
                                                        await db.save(ge)
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
                                        giveaway_entry = await db.find(table, {"status":"Active","endtime":e.endtime, "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                        for ge in giveaway_entry:
                                            if (ge.guildid == guild.id) and (ge.giveawaynum == gid):
                                                if ge.status == "Active":
                                                    ge.status = "Ended"
                                                    await db.save(ge)
                                        return
                                            
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
                                            giveaway_entry = await db.find(table, {"status":"Active", "endtime":e.endtime, "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                            for ge in giveaway_entry:
                                                if (ge.guildid == guild.id) and (ge.giveawaynum == gid):
                                                    if ge.status == "Active":
                                                        ge.status = "Ended"
                                                        await db.save(ge)
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
                                        giveaway_entry = await db.find(table, {"status":"Active", "endtime":e.endtime, "guildid":guild.id, "prize":prize, "giveawaynum":gid})
                                        for ge in giveaway_entry:
                                            if (ge.guildid == guild.id) and (ge.giveawaynum == gid):
                                                if ge.status == "Active":
                                                    ge.status = "Ended"
                                                    await db.save(ge)
                                        return

def setup(bot):
    bot.add_cog(Giveaways(bot))
    print('giveaway module loaded')
