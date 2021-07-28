import discord
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Greedy, Converter, BadArgument
from discord.ext import commands
from customchecks import *
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import re


class OnError(commands.Cog):
    """Moderation module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = Embed(description=f":x: {ctx.author.mention} You don't have permissions to perform that action",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.RoleNotFound):
            embed = Embed(description=f":x: Couldn't find that role",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.UserNotFound):
            embed = Embed(description=f":x: User not found",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                description=f":x: Command **{ctx.command.name}** on cooldown, try again later.",
                color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, ModuleNotActivatedInGuild):
            embed = Embed(description=f":x: Module for this command is not activated in the guild.",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, CommandNotActivatedInGuild):
            embed = Embed(description=f":x: Command is not activated in the guild.",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingRole):
            embed = Embed(description=f":x: {ctx.author.mention} You don't have role required to use this command.",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, missing_role):
            def gr(guild, command):
                cluster = Mongo.connect()
                db = cluster["giffany"]
                table = db['hasrole']
                regx = re.compile(f"^{command.qualified_name}$", re.IGNORECASE)
                roleid = table.find({"guildid":guild.id, "command":regx})
                for role in roleid:
                    return role['role']
                return None
            roleid = gr(ctx.guild, ctx.command)
            if roleid != None:
                role = ctx.guild.get_role(roleid)
                embed = Embed(description=f":x: {ctx.author.mention} You don't have role {role.mention} that's required to use this command.",
                              color=0xDD2222)
                await ctx.send(embed=embed)

        if isinstance(error, UserInBlacklist):
            embed = Embed(description=f":x: {ctx.author.mention} You are blacklisted from using some commands",
                          color=0xDD2222)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OnError(bot))
    print('errors module loaded')
