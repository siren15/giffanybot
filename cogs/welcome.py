import discord
from datetime import datetime
import pymongo
from pymongo import MongoClient
from mongo import *
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from discord.ext import commands
from discord.utils import get
from customchecks import *

class Welcomer(commands.Cog):
    """Welcomer module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if iscogactive(member.guild, 'welcomer') == True:
            def channelmsg(msg):
                word = [t for t in msg.split() if t.startswith('#')]
                for word in word:
                    word = word
                chname = word.replace('#', '')
                channel = get(member.guild.channels, name=chname)
                chmsg = msg.replace('word', f'{channel.mention}')
                if chmsg:
                    return chmsg
                else:
                    return msg


            try:
                if is_event_active(member.guild, 'welcome_card') == True:
                    from PIL import Image, ImageOps, ImageDraw, ImageFont
                    import os
                    import requests

                    def round(im):
                        im = im.resize((224, 224));
                        mask = Image.new("L", im.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0,0)+im.size, fill=255)
                        out = ImageOps.fit(im, mask.size, centering=(0.5,0.5))
                        out.putalpha(mask)
                        return out

                    avatarurl = f'https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.png'
                    pfp = Image.open(requests.get(avatarurl, stream=True).raw)
                    output = round(pfp)
                    output.save(f'pfp_{member.id}.png')

                    IW, IH = (1100, 500)

                    background = Image.open('card.png')
                    pfp = Image.open(f'pfp_{member.id}.png')
                    background.alpha_composite(pfp, dest=(438, 80), source=(0, 0))
                    background.save(f'wc_{member.id}.png')
                    card = Image.open(f'wc_{member.id}.png')
                    circle = Image.open('circle.png')
                    card.alpha_composite(circle, dest=(433, 75), source=(0, 0))
                    card.save(f'welcomecard_{member.id}.png')

                    img = Image.open(f'welcomecard_{member.id}.png')
                    I1 = ImageDraw.Draw(img)
                    font = ImageFont.truetype('GnuUnifontFull-Pm9P.ttf', 55)

                    msg1 = f"{member} arrived\nMember #{len(member.guild.members)}"
                    #msg2 = f"""Member #{len(ctx.guild.members)}"""

                    tw, th = I1.textsize(msg1, font)
                    #tw2, th2 = I1.textsize(msg2, font)

                    I1.text(((IW-tw)/2,(IH-th)/1.1), msg1, font=font, stroke_width=2, stroke_fill=(30, 27, 26), align="center", fill=(255, 255, 255))
                    #I1.text(((IW-tw2)/2,(IH-th2)/1.3), msg2, font=font, fill=(255, 255, 255))
                    img.save(f"wcard_{member.id}.png")

                    file = discord.File(fp=f'wcard_{member.id}.png')

                    db = await odm.connect()
                    channel_id  = await db.find(welcomer, welcomer.guildid==member.guild.id)
                    for ch in channel_id:
                        channelid = ch.channelid
                        channel = member.guild.get_channel(int(channelid))
                    try:
                        if is_event_active(member.guild, 'welcome_message') == True:
                            welcome_message = await db.find(welcomer, welcomer.guildid==member.guild.id, welcomer.channelid==channelid)
                            for wm in welcome_message:
                                welcome_message = wm.msg
                                guild = member.guild
                                mention = member.mention
                                await channel.send(welcome_message.format(guild=guild, user=member, member=mention), file=file)
                    except EventNotActivatedInGuild:
                        await channel.send(file=file)
                    os.remove(f'welcomecard_{member.id}.png')
                    os.remove(f'wcard_{member.id}.png')
                    os.remove(f'pfp_{member.id}.png')
                    os.remove(f'wc_{member.id}.png')

            except EventNotActivatedInGuild:
                if is_event_active(member.guild, 'welcome_message') == True:
                    db = await odm.connect()
                    channel_id  = await db.find(welcomer, welcomer.guildid==member.guild.id)
                    for ch in channel_id:
                        channelid = ch.channelid
                        channel = member.guild.get_channel(int(channelid))

                    welcome_message = await db.find(welcomer, welcomer.guildid==member.guild.id, welcomer.channelid==channelid)
                    for wm in welcome_message:
                        welcome_message = wm.msg
                        guild = member.guild
                        mention = member.mention
                        try:
                            is_event_active(member.guild, 'welcome_card')
                        except EventNotActivatedInGuild:
                            await channel.send(welcome_message.format(guild=guild, user=member, member=mention))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id == 149167686159564800:
            if iscogactive(before.guild, 'welcomer') == True:
                if is_event_active(before.guild, 'advanced_welcome_message'):
                    db = await odm.connect()
                    channel_id  = await db.find_one(welcomer, {"guildid":before.guild.id})
                    channelid = channel_id.achannelid
                    channel = get(before.guild.channels, id=channelid)

                    wm = await db.find_one(welcomer, {"guildid":before.guild.id, "channelid":channelid})
                    welcome_message = wm.amsg

                    limborole = get(before.guild.roles, name="Limbo")
                    muted = get(before.guild.roles, name="Muted")

                    if limborole in before.roles:
                        return

                    if muted in before.roles:
                        return

                    users = await db.find_one(persistentroles, {"guildid":before.guild.id, "userid":before.id})
                    if before.id == users.userid:
                        return

                    if len(before.roles) < len(after.roles):
                        newRole = next(role for role in after.roles if role not in before.roles)
                        if newRole.name == "Gravity Falls Citizens":
                            member_mention = before.mention
                            user = before
                            guild = before.guild
                            await channel.send(str(welcome_message).format(guild=guild, user=user, member=member_mention))

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def welcome(self, ctx):
        """Sets welcome channel and message. Use:.welcome channel <channel> and .welcome message <message>"""
        embed = discord.Embed(description=f"Available setup commands: \n`.welcome channel <channel>` to assign channel for welcome message\n`.welcome message` to start welcome message creation process",
                              timestamp=datetime.datetime.utcnow(),
                              color=0xF893B2)
        await ctx.send(embed=embed)

    @welcome.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def channel(self, ctx, *, channel: discord.TextChannel):
        if channel == None:
            embed = Embed(
                description=":x: Please provide a channel",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['welcomer']

        def gld(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            glds = db['welcomer'].find({"guildid":guild.id})
            for g in glds:
                id = g['guildid']
                return id
            return None

        gld = gld(ctx.guild)

        def chids(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            channelids = db['welcomer'].find({"guildid":guild.id})
            for channel in channelids:
                id = channel['channelid']
                return id
            return None

        old_channel = chids(ctx.guild)
        if gld == None:
            table.insert_one({"guildid":ctx.guild.id, "channelid":channel.id})
            embed = discord.Embed(description=f"Channel for welcome message has been set to {channel.mention}",
                                  color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            if old_channel != None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"channelid":channel.id}})
                embed = discord.Embed(description=f"Channel for welcome message has been updated to {channel.mention}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

            elif old_channel == None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"channelid":channel.id}})
                embed = discord.Embed(description=f"Channel for welcome message has been set to {channel.mention}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

    @welcome.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def message(self, ctx, *, msg=None):
        if msg == None:
            embed = Embed(
                description=":x: Please provide welcome message",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['welcomer']

        def gld(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            glds = db['welcomer'].find({"guildid":guild.id})
            for g in glds:
                id = g['guildid']
                return id
            return None

        gld = gld(ctx.guild)

        def message(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            msg = db['welcomer'].find({"guildid":guild.id})
            for m in msg:
                message = m['msg']
                return message
            return None

        old_msg = message(ctx.guild)

        if gld == None:
            table.insert_one({"guildid":ctx.guild.id, "msg":msg})
            embed = discord.Embed(description=f"**__Welcome message has been set to:__**\n\n{msg}",
                                  color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            if old_msg != None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"msg":msg}})
                embed = discord.Embed(description=f"**__Welcome message has been updated to:__**\n\n{msg}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

            elif old_msg == None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"msg":msg}})
                embed = discord.Embed(description=f"**__Welcome message has been set to:__**\n\n{msg}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcomer(bot))
    print('welcomer module loaded')
