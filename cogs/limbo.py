import discord
import dataset
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from datetime import datetime
from customchecks import *
from discord import Embed
from discord.ext import commands
from discord.utils import get
from stuf import stuf

class Limbo(commands.Cog):
    """Limbo module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("limbo")
    async def limbo(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        """Put member to limbo. Use: .limbo <member> <reason>"""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['limbo']
        def field(item, member, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            results = db['limbo'].find({"memberid":member.id, "guildid":guild.id})
            for r in results:
                return r[f'{item}']
            return None

        limborole = get(ctx.guild.roles, name="Limbo")
        member_id = field('memberid', member, ctx.guild)
        member_roles = [role.mention for role in member.roles]
        member_roles = ','.join(member_roles)
        member_roles = member_roles.replace('<', '')
        member_roles = member_roles.replace('@', '')
        member_roles = member_roles.replace('&', '')
        member_roles = member_roles.replace('>', '')

        if member == None:
            embed = Embed(description=f":x: Please provide a member!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if (limborole in member.roles and member_id == member.id) or (member_id == member.id):
            if member == ctx.message.author:
                embed = Embed(description=f":x: You can't unlimbo yourself!",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

            if limborole in member.roles and member_id != member.id:
                await member.remove_roles(limborole, reason=reason)
                embed = discord.Embed(description=f"{member} **was released from limbo**\n**For:** {reason}",
                                      timestamp=datetime.utcnow(),
                                      color=0xF893B2)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

            role_ids = field('member_roles', member, ctx.guild)
            roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

            if roles in member.roles:
                embed = Embed(description=f":x: Can't give {member.mention} roles they already have",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

            await member.edit(roles=roles)
            await member.remove_roles(limborole, reason=reason)
            table.delete_one({"guildid":ctx.guild.id, "memberid":member.id})
            embed = discord.Embed(description=f"{member} **was released from limbo**\n**For:** {reason}",
                                  timestamp=datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.set_footer(text=f'User ID: {member.id}')
            await ctx.send(embed=embed)
        elif (limborole not in member.roles and member_id != member.id) or (member_id != member.id):
            if member == ctx.message.author:
                embed = Embed(description=f":x: You can't limbo yourself!",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

            table.insert_one({"guildid":ctx.guild.id, "memberid":member.id, "member_roles":member_roles})

            await member.edit(roles=[])
            await member.add_roles(limborole, reason=reason)
            limbo_channel = get(ctx.guild.channels, name='limbo')
            embed = discord.Embed(description=f"{member} **was thrown to limbo**\n**For:** {reason}",
                                  timestamp=datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.set_footer(text=f'User ID: {member.id}')
            await ctx.send(embed=embed)

    @limbo.command()
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("limbo")
    async def add(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Put member to limbo. Use: .limbo add <member> <reason>"""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['limbo']

        def field(item, member, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            results = db['limbo'].find({"memberid":member.id, "guildid":guild.id})
            for r in results:
                return r[f'{item}']
            return None

        limborole = get(ctx.guild.roles, name="Limbo")
        member_id = field('memberid', member, ctx.guild)
        member_roles = [role.mention for role in member.roles]
        member_roles = ','.join(member_roles)
        member_roles = member_roles.replace('<', '')
        member_roles = member_roles.replace('@', '')
        member_roles = member_roles.replace('&', '')
        member_roles = member_roles.replace('>', '')

        if member == ctx.message.author:
            embed = Embed(description=f":x: You can't limbo yourself!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == None:
            embed = Embed(description=f":x: Please provide a member!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if (limborole in member.roles) or (member_id == member.id):
            embed = Embed(description=f":x: {member.mention} is already limboed",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        table.insert_one({"guildid":ctx.guild.id, "memberid":member.id, "member_roles":member_roles})

        await member.edit(roles=[])
        await member.add_roles(limborole, reason=reason)
        limbo_channel = get(ctx.guild.channels, name='limbo')
        embed = discord.Embed(description=f"{member} **was thrown to limbo**\n**For:** {reason}",
                              timestamp=datetime.utcnow(),
                              color=0xF893B2)
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.set_footer(text=f'User ID: {member.id}')
        await ctx.send(embed=embed)

    @limbo.command()
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("limbo")
    async def remove(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Releases member from limbo. Use: .limbo remove <member>"""
        limborole = get(ctx.guild.roles, name="Limbo")
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['limbo']

        def field(item, member, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            results = db['limbo'].find({'memberid':member.id, 'guildid':guild.id})
            for r in results:
                return r[f'{item}']
            return None

        member_id = field('memberid', member, ctx.guild)

        if member == ctx.message.author:
            embed = Embed(description=f":x: You can't unlimbo yourself!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == None:
            embed = Embed(description=f":x: Please provide a member!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if (limborole not in member.roles) or (member.id != member_id):
            embed = Embed(description=f":x: {member.mention} is not in limbo",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if (limborole in member.roles) or (member.id == member_id):

            role_ids = field('member_roles', member, ctx.guild)
            roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

            if roles in member.roles:
                embed = Embed(description=f":x: Can't give {member.mention} roles they already have",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return

            await member.edit(roles=roles, reason=reason)
            table.delete_one({"guildid":ctx.guild.id, "memberid":member.id})
            embed = discord.Embed(description=f"{member} **was released from limbo**\n**For:** {reason}",
                                  timestamp=datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.set_footer(text=f'User ID: {member.id}')
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id == 149167686159564800:
            def chids(guild):
                cluster = Mongo.connect()
                db = cluster["giffany"]
                channelids = db['logs'].find({"guild_id":guild.id})
                for channel in channelids:
                    id = channel['channel_id']
                    return id
                return None

            log_ch_from_db = chids(message.guild)
            log_channel = message.guild.get_channel(int(log_ch_from_db))

            if message.channel.id == 736680179253903491:
                embed = discord.Embed(title="Limbo log", timestamp=datetime.utcnow(), color=0xF893B2)
                embed.set_thumbnail(url=f'{message.author.avatar_url}')
                embed.add_field(name=f"{message.author}", value=f"{message.content}", inline=False)
                embed.set_footer(text=f'User ID: {message.author.id}')
                await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Limbo(bot))
    print('limbo module loaded')
