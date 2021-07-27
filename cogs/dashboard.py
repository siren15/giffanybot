from datetime import datetime
from random import choice, randint
from typing import Optional


import discord
from aiohttp import request
from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument, CheckFailure
from discord.ext.commands import command, cooldown
from customchecks import *

class dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['settings'])
    async def dashboard(self, ctx):
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

        def newpage(prefix, acm, inacm, ace, inace, guild, pages):
            embed = Embed(description=f"__**Settings for {guild}**__",
            colour=0xF893B2)
            embed.add_field(name="Prefix:", value=f"{prefix}", inline=False)
            embed.add_field(name="Active modules:", value=f"{acm}", inline=False)
            embed.add_field(name="Inactive modules:", value=f"{inacm}", inline=False)
            embed.add_field(name="Active events:", value=f"{ace}", inline=False)
            embed.add_field(name="Inactive events:", value=f"{inace}", inline=False)
            embed.set_footer(text=pages)
            return embed

        def field(fld):
            field = ''
            for i in fld:
                field = field + f"\n{i},"

            return f

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['prefixes']

        names = db.query('SELECT name FROM giveme WHERE guildid = {0}'.format(ctx.guild.id))
        req_names = db.query('SELECT ignorename FROM giveme WHERE guildid = {0}'.format(ctx.guild.id))
        ignore_names = db.query('SELECT ignorename FROM giveme WHERE guildid = {0}'.format(ctx.guild.id))


        names = [name['name']+"\n" for name in names]
        req = [name['ignorename']+"\n" for name in req_names]
        ignored = [name['ignorename']+"\n" for name in ignore_names]

        if names == []:
            embed = Embed(description=f"There are no givemes for {ctx.guild}.",
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
    bot.add_cog(dashboard(bot))
    print('dashboard module loaded')
