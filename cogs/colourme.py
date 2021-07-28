import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional
import discord
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CommandNotFound
from customchecks import *
from discord.utils import get

class colourme(commands.Cog):
    """Give yourself a colour role from colour roles on the list."""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['colorme'], invoke_without_command=True)
    @has_active_cogs("colourme")
    @is_user_blacklisted()
    async def colourme(self, ctx, *, colourme_name=None, member: discord.Member=None):
        """Give yourself a colour role from predefined list of roles. You are able to have just one."""
        if member == None:
            member = ctx.message.author

        elif member != None:
            member = ctx.message.author

        if colourme_name == None:
            embed = Embed(
                description=":x: Please provide a colourme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def names(guild, colourme_name):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{colourme_name}$", re.IGNORECASE)
            names = db['colourme'].find({"name":regx, "guildid":guild.id})
            for n in names:
                name = n['name'].lower()
                return name
            return None

        def role_ids(colourme_name, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{colourme_name}$", re.IGNORECASE)
            search = db['colourme'].find({"name":regx, "guildid":guild.id})
            for se in search:
                s = se[f'roleid']
                return s
            return None

        def req_ids(colourme_name, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{colourme_name}$", re.IGNORECASE)
            search = db['colourme'].find({"name":regx, "guildid":guild.id})
            for se in search:
                s = se[f'reqid']
                return s
            return None

        def ignore_ids(colourme_name, guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{colourme_name}$", re.IGNORECASE)
            search = db['colourme'].find({"name":regx, "guildid":guild.id})
            for se in search:
                s = se[f'ignoreid']
                return s
            return None

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['colourme']
        all_roles = table.find({"guildid":ctx.guild.id})
        all_roles = [id['roleid'] for id in all_roles]

        names = names(ctx.guild, colourme_name)
        roleids = role_ids(colourme_name, ctx.guild)
        reqids = req_ids(colourme_name, ctx.guild)
        ignoreids = ignore_ids(colourme_name, ctx.guild)

        if names != colourme_name.lower():
            embed = Embed(
                description=f":x: Couldn't find `{colourme_name}` as a colourme for {ctx.guild}",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        roles = get(ctx.guild.roles, id=roleids)
        req = get(ctx.guild.roles, id=reqids)
        ignore = get(ctx.guild.roles, id=ignoreids)

        if ignore in member.roles:
            embed = Embed(
                description=f":x: You have role {ignore.mention} which is ignored for this colourme",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if (req == None) or (req in member.roles):
            if names == colourme_name.lower():
                if roles in member.roles:
                    await member.remove_roles(roles)
                    embed = discord.Embed(
                        description=f"I have removed {roles.mention} from {member.mention}",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
                elif roles not in member.roles:
                    old_role = [role for role in member.roles if role.id in all_roles]
                    for old_role in old_role:
                        old_role = old_role
                    if old_role in member.roles:
                        await member.remove_roles(old_role)
                    await member.add_roles(roles)
                    embed = discord.Embed(
                        description=f"I have assigned {roles.mention} to {member.mention}",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: You don't have role {req.mention} required for this colourme",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @colourme.command(aliases=['add'])
    @has_active_cogs("colourme")
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, name=None, colourme_role: discord.Role=None, optional_role_req:discord.Role=None, *, optional_role_ignore:discord.Role=None):
        """Create a colourme for members to use."""
        if name is None:
            embed = Embed(
                description=":x: Please provide a colourme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def names(guild, name):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            regx = re.compile(f"^{name}$", re.IGNORECASE)
            names = db['colourme'].find({"name":regx, "guildid":guild.id})
            for n in names:
                name = ''
                name = name + f"{n['name'].lower()}"
                return name
            return None

        rolenames = names(ctx.guild, name)

        if name.lower() == rolenames:
            embed = Embed(description=f":x: colourme with the name `{name}` already exists",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if colourme_role == None:
            embed = Embed(
                description=":x: Please provide a colourme role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        else:
            role_id = colourme_role.id
            role_name = colourme_role

        if optional_role_req == None:
            req_id = None
            req_name = None
        else:
            req_id = optional_role_req.id
            req_name = optional_role_req

        if optional_role_ignore == None:
            ignore_id = None
            ignore_name = None
        else:
            ignore_id = optional_role_ignore.id
            ignore_name = optional_role_ignore

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['colourme']
        table.insert_one({"guildid":ctx.guild.id, "reqname":str(req_name), "reqid":req_id, "ignorename":str(ignore_name), "ignoreid":ignore_id, "name":str(name), "rolename":str(role_name), "roleid":role_id})
        embed = discord.Embed(description=f"colourme `{name}` created \nRequired role: {req_name} \nIgnored role: {ignore_name}",
                              timestamp=datetime.utcnow(),
                              color=0xF893B2)
        embed.set_footer(text=f'created by: {ctx.author}|{ctx.author.id}')
        await ctx.send(embed=embed)

    @colourme.command(aliases=['remove'])
    @has_active_cogs("colourme")
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        """Delete colourme from list."""
        if name == None:
            embed = Embed(
                description=":x: Please provide a colourme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['colourme']

        names = table.find({"name":name, "guildid":ctx.guild.id})
        names = [n['name'] for n in names]
        if names == []:
            embed = Embed(description=f":x: I couldn't find a colourme with the name **{name}**",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        else:
            table.delete_one({"guildid":ctx.guild.id, "name":name})
            embed = discord.Embed(description=f"colourme **{name}** removed",
                                  timestamp=datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_footer(text=f'removed by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)


    @colourme.command()
    @has_active_cogs("colourme")
    @is_user_blacklisted()
    async def list(self, ctx):
        """List all the colourmes you can use."""
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

        def newpage(names, req, ignored, guild, pages):
            embed = Embed(description=f"__**List of all the colourmes for {guild}**__",
            colour=0xF893B2)
            embed.add_field(name="Colourme names:", value=f"{names}", inline=True)
            embed.add_field(name="Required roles:", value=f"{req}", inline=True)
            embed.add_field(name="Ignored roles:", value=f"{ignored}", inline=True)
            embed.set_footer(text=pages)
            return embed

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['colourme']

        names = table.find({"guildid":ctx.guild.id})
        req = table.find({"guildid":ctx.guild.id})
        ignored = table.find({"guildid":ctx.guild.id})
        names = [name['name']+"\n" for name in names]
        req = [str(name['reqname'])+"\n" for name in req]
        ignored = [str(name['ignorename'])+"\n" for name in ignored]

        if names == []:
            embed = Embed(description=f"There are no colourmes for {ctx.guild}.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1

        nc = list(chunks(names, 10))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(create_list(names, 10, s, e), create_list(req, 10, s, e), create_list(ignored, 10, s, e), ctx.guild, footer))
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
                await embedl.edit(embed=newpage(create_list(names, 10, s, e), create_list(req, 10, s, e), create_list(ignored, 10, s, e), ctx.guild, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(create_list(names, 10, s, e), create_list(req, 10, s, e), create_list(ignored, 10, s, e), ctx.guild, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)

def setup(bot):
    bot.add_cog(colourme(bot))
    print('colourme module loaded')
