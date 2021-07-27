import asyncio
import re
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from datetime import datetime, timedelta
from typing import Optional
import discord

from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Greedy, Converter, CommandNotFound
from customchecks import *
from discord.utils import get

class giverole(commands.Cog):
    """Give member a role from existing roles in the guild."""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giverole")
    async def role(self, ctx, member: discord.Member = None, *, role:discord.Role=None):
        """Give member a role."""
        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if role == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                description=f"I have removed {roles.mention} from {member.mention}",
                timestamp=datetime.utcnow(),
                color=0xF893B2)
            embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)
        elif role not in member.roles:
            await member.add_roles(role)
            embed = discord.Embed(
                description=f"I have assigned {roles.mention} to {member.mention}",
                timestamp=datetime.utcnow(),
                color=0xF893B2)
            embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)

    @role.command(aliases=['add'])
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giverole")
    async def give(self, ctx, member: discord.Member = None, roles: Greedy[discord.Role]=None):
        """Give member roles."""
        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        r = ''
        for role in roles:
            r = r + f"{role.mention} "
            if role == None:
                embed = Embed(
                    description=":x: Please provide a role",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return

            if role not in member.roles:
                async with ctx.typing():
                    rs = member.roles + roles
                    await member.edit(roles=rs)
            else:
                if member == None:
                    embed = Embed(description=f":x: {member} already has {role} assigned",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

        embed = discord.Embed(
            description=f"I have assigned {r} to {member.mention}",
            timestamp=datetime.utcnow(),
            color=0xF893B2)
        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
        await ctx.send(embed=embed)

    @role.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giverole")
    async def remove(self, ctx, member: discord.Member = None, roles: Greedy[discord.Role]=None):
        """Remove member from roles."""
        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if not len(roles):
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        roles = [role for role in roles if role in member.roles]
        new_roles_list = [r for r in member.roles if r not in roles]
        if roles:
            r = ''
            for role in roles:
                r = r + f"{role.mention} "
                async with ctx.typing():
                    await member.edit(roles=new_roles_list)

            embed = discord.Embed(
                description=f"I have removed {r} from {member.mention}",
                timestamp=datetime.utcnow(),
                color=0xF893B2)
            embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)

    @role.command(aliases=['addall', 'addeveryone'])
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giverole")
    async def giveall(self, ctx, *, role:discord.Role=None):
        """Give everyone in the server a role."""
        everyone = ctx.guild.members
        for member in everyone:
            if role == None:
                embed = Embed(
                    description=":x: Please provide a role",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return

            if role not in member.roles:
                async with ctx.typing():
                    await member.add_roles(roles)

        embed = discord.Embed(
            description=f"I have assigned {roles.mention} to everyone.",
            timestamp=datetime.utcnow(),
            color=0xF893B2)
        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
        await ctx.send(embed=embed)

    @role.command(aliases=['removeeveryone'])
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giverole")
    async def removeall(self, ctx, *, role:discord.Role=None):
        """Remove everyone in the server from a role."""
        everyone = ctx.guild.members
        for member in everyone:
            if role == None:
                embed = Embed(
                    description=":x: Please provide a role",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return

            if role in member.roles:
                async with ctx.typing():
                    await member.remove_roles(roles)

        embed = discord.Embed(
            description=f"I have removed {roles.mention} from everyone.",
            timestamp=datetime.utcnow(),
            color=0xF893B2)
        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(giverole(bot))
    print('giverole module loaded')
