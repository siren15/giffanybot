import discord
from datetime import datetime
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from discord.ext import commands
from discord.utils import get
from customchecks import *
from motor.motor_asyncio import AsyncIOMotorClient

class Welcomer(commands.Cog):
    """Welcomer module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if iscogactive(member.guild, 'welcomer') == True:
            if is_event_active(member.guild, 'leave_message') == True:
                db = await odm.connect()
                channel_id  = await db.find(welcomer, welcomer.guildid==member.guild.id)
                for ch in channel_id:
                    channelid = ch.leavechannelid
                    channel = member.guild.get_channel(int(channelid))
                    leave_message = await db.find(welcomer, welcomer.guildid==member.guild.id, welcomer.channelid==channelid)
                    for wm in leave_message:
                        leave_message = wm.leavemsg
                        guild = member.guild
                        mention = member.mention

                        await channel.send(leave_message.format(guild=guild, user=member, member=mention))

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def leave(self, ctx):
        """Sets leave channel and message. Use:.leave channel <channel> and .leave message <message>"""
        embed = discord.Embed(description=f"Available setup commands: \n`.leave channel <channel>` to assign channel for leave message\n`.leave message` to start leave message creation process",
                              timestamp=datetime.datetime.utcnow(),
                              color=0xF893B2)
        await ctx.send(embed=embed)

    @leave.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def channel(self, ctx, *, channel: discord.TextChannel):
        if channel == None:
            embed = Embed(
                description=":x: Please provide a channel",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        dcluster = Mongo.connect()
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
                id = channel['leavechannelid']
                return id
            return None

        old_channel = chids(ctx.guild)
        if gld == None:
            table.insert_one({"guildid":ctx.guild.id, "leavechannelid":channel.id})
            embed = discord.Embed(description=f"Channel for leave message has been set to {channel.mention}",
                                  color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            if old_channel != None:
                table.update_one({"guildid":ctx.guild.id, "leavechannelid":channel.id}, {"$set":{"leavechannelid":channel.id}})
                embed = discord.Embed(description=f"Channel for leave message has been updated to {channel.mention}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

            elif old_channel == None:
                table.update_one({"guildid":ctx.guild.id, "leavechannelid":channel.id}, {"$set":{"leavechannelid":channel.id}})
                embed = discord.Embed(description=f"Channel for leave message has been set to {channel.mention}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

    @leave.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("welcomer")
    async def message(self, ctx, *, msg=None):
        if msg == None:
            embed = Embed(
                description=":x: Please provide leave message",
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
                message = m['leavemsg']
                return message
            return None

        old_msg = message(ctx.guild)

        if gld == None:
            table.insert_one({"guildid":ctx.guild.id, "leavemsg":msg})
            embed = discord.Embed(description=f"**__Leave message has been set to:__**\n\n{msg}",
                                  color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            if old_msg != None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"leavemsg":msg}})
                embed = discord.Embed(description=f"**__Leave message has been updated to:__**\n\n{msg}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)

            elif old_msg == None:
                table.update_one({"guildid":ctx.guild.id}, {"$set":{"leavemsg":msg}})
                embed = discord.Embed(description=f"**__Leave message has been set to:__**\n\n{msg}",
                                      color=0xF893B2)
                await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Welcomer(bot))
    print('welcomer module loaded')
