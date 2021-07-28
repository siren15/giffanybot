import discord
from datetime import datetime
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import asyncio
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CheckFailure
from customchecks import *
import re


class UserFilter(commands.Cog):
    """[Mods] Filter users from being able to use some commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['uf', 'userfilter'], invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def blacklist(self, ctx):
        embed = Embed(description="This command adds users to a blacklist so that they can't use some commands. \nTo add someone to blacklist use: `.blacklist add 'member'` \nTo remove use: `.blacklist remove 'member'`\nAliases: `.uf`, `.userfilter`",
                      colour=0xF893B2
        )
        await ctx.send(embed=embed)

    @blacklist.command()
    @commands.has_permissions(ban_members=True)
    async def add(self, ctx, member: discord.Member=None, *, reason=None):
        if ctx.message.author.top_role.position == member.top_role.position:
            embed = Embed(description=f":x: You can't mute people with the same rank as you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position < member.top_role.position:
            embed = Embed(description=f":x: You can't mute people with higher rank then you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['userfilter']
        if member == ctx.author:
            embed = Embed(
              description=":x: You cannot filter yourself!",
              color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == None:
            embed = Embed(
              description=":x: Please provide a user!",
              color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if reason == None:
            reason = "No reason provided."

        def uf(guild, member):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            users = db['userfilter'].find({"guild":guild.id, "user":member.id})
            for u in users:
                user = u['user']
                return user
            return None

        user = uf(ctx.guild, member)

        if user == member.id:
            embed = Embed(
              description=f":x: {member} is already blacklisted!",
              color=0xDD2222)
            await ctx.send(embed=embed)
            return
        else:
            table.insert_one({"guild":ctx.guild.id, "user":member.id})
            embed = discord.Embed(
              description=f"**{member}|{member.id}** was added to commands blacklist \n**For:** {reason}",
              timestamp=datetime.utcnow(),
              color=0xF893B2)
            embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)

    @blacklist.command(aliases=['filterremove', 'whitelist', 'fdelete', 'filterdelete'])
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, member: discord.Member = None, *, reason=None):
      cluster = Mongo.connect()
      db = cluster["giffany"]
      table = db['userfilter']
      def uf(guild, member):
          cluster = Mongo.connect()
          db = cluster["giffany"]
          users = db['userfilter'].find({"guild":guild.id, "user":member.id})
          for u in users:
              user = u['user']
              return user
          return None

      user = uf(ctx.guild, member)

      if user == ctx.author:
          embed = Embed(
              description=":x: You can't remove yourself from the blacklist!",
              color=0xDD2222)
          await ctx.send(embed=embed)
          return

      if member == None:
          embed = Embed(
              description=":x: Please provide a member!",
              color=0xDD2222)
          await ctx.send(embed=embed)
          return

      if reason == None:
          reason = "No reason provided."

      if user != member.id:
          embed = Embed(
              description=f":x: **{member}** not blacklisted",
              color=0xDD2222)
          await ctx.send(embed=embed)
          return
      else:
          table.delete_one({"guild":ctx.guild.id, "user":member.id})
          embed = discord.Embed(description=f"**{member}|{member.id}** was removed from blacklist \n**For:** {reason}",
                                timestamp=datetime.utcnow(),
                                color=0xF893B2)
          embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
          await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UserFilter(bot))
    print('user filter module loaded')
