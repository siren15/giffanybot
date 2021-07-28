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
from discord.ext.commands import Greedy, CommandNotFound
from customchecks import *

class giveyou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("giveyou")
    async def giveyou(self, ctx, member: discord.Member=None, *, giveyou_name=None):
        """This command allows mods who normally do not have permissions to assign roles, to assign preset roles to users. Assigning a giveyou to a member who already has the role will remove it.
           Use: .giveyou <member(s)> <name>"""
        if giveyou_name == None:
            embed = Embed(
                description=":x: Please provide a giveyou name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def field(item, giveyou_name, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{giveyou_name}$", re.IGNORECASE)
            results = db['giveyou'].find({"name":regx, "guildid":guild.id})
            for r in results:
                return r[f'{item}']
            return None

        name = field('name', giveyou_name, ctx.guild)
        roleid = field('roleid', giveyou_name, ctx.guild)

        if name != giveyou_name.lower():
            embed = Embed(
                description=f":x: Couldn't find `{giveyou_name}` as a giveyou for {ctx.guild}",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        role = [role for role in ctx.guild.roles if role.id == roleid]
        for role in role:
            role = role

        if name == giveyou_name.lower():
            if role in member.roles:
                await member.remove_roles(role)
                embed = discord.Embed(
                    description=f"I have removed {role.mention} from {member.mention}",
                    color=0xF893B2)
                await ctx.send(embed=embed)
            elif role not in member.roles:
                await member.add_roles(role)
                embed = discord.Embed(
                    description=f"I have assigned {role.mention} to {member.mention}",
                    color=0xF893B2)
                await ctx.send(embed=embed)

    @giveyou.command(aliases=['add'])
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giveyou")
    async def create(self, ctx, name=None, *, giveyou_role:discord.Role=None):
        """(Admin only)Create giveyous. Use: .giveyou create <name> <role(case sensitive)>"""
        if name is None:
            embed = Embed(
                description=":x: Please provide a giveyou name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def names(guild, name):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{name}$", re.IGNORECASE)
            names = db['giveyou'].find({"name":regx, "guildid":guild.id})
            for n in names:
                name = ''
                name = name + f"{n['name'].lower()}"
                return name
            return None

        rolenames = names(ctx.guild, name)

        if name.lower() == rolenames:
            embed = Embed(description=f":x: giveyou with the name `{name}` already exists",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if giveyou_role == None:
            embed = Embed(
                description=":x: Please provide a giveyou role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        else:
            role_id = giveyou_role.id
            role_name = giveyou_role

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['giveyou']
        table.insert_one({"guildid":int(ctx.guild.id), "name":str(name), "rolename":str(role_name), "roleid":int(role_id)})
        embed = discord.Embed(description=f"giveyou `{name}` created",
                              timestamp=datetime.utcnow(),
                              color=0xF893B2)
        embed.set_footer(text=f'created by: {ctx.author}|{ctx.author.id}')
        await ctx.send(embed=embed)

    @giveyou.command(aliases=['remove'])
    @commands.has_permissions(administrator=True)
    @has_active_cogs("giveyou")
    async def delete(self, ctx, name=None):
        """(Admin only)Remove giveyous. Use: .giveyou remove <name>"""
        if name == None:
            embed = Embed(
                description=":x: Please provide a giveyou name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['giveyou']

        names = table.find({"name":name, "guildid":ctx.guild.id})
        names = [n['name'] for n in names]
        if names == []:
            embed = Embed(description=f":x: I couldn't find a giveyou with the name **{name}**",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        else:
            table.delete_one({"guildid":ctx.guild.id, "name":name})
            embed = discord.Embed(description=f"giveyou **{name}** removed",
                                  timestamp=datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_footer(text=f'removed by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)

    @giveyou.command()
    @commands.has_permissions(manage_messages=True)
    @has_active_cogs("giveyou")
    async def list(self, ctx):
        """List all the giveyous you can use."""
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

        def newpage(names, roles, guild, pages):
            embed = Embed(description=f"__**List of all the giveyous for {guild}**__",
            colour=0xF893B2)
            embed.add_field(name="Giveyou names:", value=f"{names}", inline=True)
            embed.add_field(name="Giveyou roles:", value=f"{roles}", inline=True)
            embed.set_footer(text=pages)
            return embed

        def field(fld):
            field = ''
            for i in fld:
                field = field + f"\n{i},"

            return f

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['colourme']

        names = table.find({"guildid":ctx.guild.id})
        names = [str(name['name'])+"\n" for name in names]

        roles = table.find({"guildid":ctx.guild.id})
        roles = [str(name['rolename'])+"\n" for name in roles]

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

def setup(bot):
    bot.add_cog(giveyou(bot))
    print('giveyou module loaded')
