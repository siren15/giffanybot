import discord
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import datetime
import asyncio
import re
import requests
from typing import Optional
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CheckFailure
from discord.utils import get
from stuf import stuf
from customchecks import *


class Tags(commands.Cog):
    """Tags module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['t'], invoke_without_command=True)
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("tags")
    async def tag(self, ctx, *,tag_Name=None):
        """let's me recall tags"""
        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = await odm.connect()
        regx = re.compile(f"^{tag_Name}$", re.IGNORECASE)
        tn = await db.find_one(tag, {"names":regx, "guild_id":ctx.channel.guild.id})

        if tn is None:
            embed = Embed(
                description=f":x: `{tag_Name}` is not a tag",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        tagscontent = await db.find_one(tag, {"names":regx, "guild_id":ctx.channel.guild.id})
        tagcontent = tagscontent.content

        if tag_Name.lower() == tn.names.lower():
            await ctx.send(f"{tagcontent}")

    @tag.command(aliases=['c'])
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("tags")
    async def create(self, ctx, tagname=None, *, content=None):
        """Lets me create tags."""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']

        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author == ctx.message.author

        if tagname != None:
            regx = re.compile(f"^{tagname}$", re.IGNORECASE)
            tagnames = table.find({"names":regx, "guild_id":ctx.channel.guild.id})
            tn = [n['names'] for n in tagnames]
            if tn != []:
                embed = Embed(
                    description=":x: Tag with that name already exists, try again",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await ctx.mesasge.delete()
                return

        if tagname != None and ctx.message.attachments:
            for url in ctx.message.attachments:
                table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":url.url})
                embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**",
                              colour=0xF893B2)
                embed.set_image(url=url.url)
                await ctx.send(embed=embed)
                return

        if tagname == None:
            embed = discord.Embed(
                description=f"Alright! Let's create a tag! First, type tag's name, or `abort` to abort the process.",
                colour=0xF893B2)
            start_embed = await ctx.send(embed=embed)

            istagname = False
            while istagname == False:
                try:
                    tagname = await self.bot.wait_for('message', timeout=60, check=check)

                except asyncio.TimeoutError:
                        embed = Embed(
                            description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 1 minutes to respond, creation cancelled.",
                            color=0xDD2222)
                        await ctx.send(embed=embed)
                        await start_embed.delete()
                        await ctx.message.delete()
                        return

                tn = tagname.content
                lowtn = tn.lower()

                if lowtn == "abort":
                    embed = Embed(
                        description=":x: Creation process aborted",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    await ctx.message.delete()
                    await start_embed.delete()
                    await tagname.delete()
                    return

                else:
                    regx = re.compile(f"^{tagname.content}$", re.IGNORECASE)
                    tagnames = table.find({"names":regx, "guild_id":ctx.guild.id})
                    tn = [n['names'] for n in tagnames]
                    if tn != []:
                        embed = Embed(
                            description=":x: Tag with that name already exists, try again",
                            color=0xDD2222)
                        await ctx.send(embed=embed)
                        await tagname.delete()
                    else:
                        istagname = True

            embed = Embed(description=f"Okay! Tag's name is `{tagname.content}`. Now please provide tag's content, or type `abort` to abort the process.",
                          colour=0xF893B2)
            tagcontent_embed = await ctx.send(embed=embed)
            try:
                tagcontent = await self.bot.wait_for('message', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 1 minute to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await ctx.message.delete()
                    await start_embed.delete()
                    await tagname.delete()
                    await tagcontent_embed.delete()
                    return


            cntnt = tagcontent.content
            lowtagcntnt= cntnt.lower()

            if lowtagcntnt == "abort":
                embed = Embed(
                    description=":x: Tag creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await ctx.message.delete()
                await start_embed.delete()
                await tagname.delete()
                await tagcontent_embed.delete()
                await tagcontent.delete()
                return
            else:
                def geturl(string):
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex,string)
                    return [x[0] for x in url]

                if tagcontent.attachments:
                    for url in tagcontent.attachments:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname.content, "content":url.url})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname.content} \n**Tag's content:**",
                                      colour=0xF893B2)
                        embed.set_image(url=url.url)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await start_embed.delete()
                        await tagname.delete()
                        await tagcontent_embed.delete()
                        return
                else:
                    url = geturl(tagcontent.content)
                    for url in url:
                        url = url
                    if url:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname.content, "content":url})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname.content} \n**Tag's content:**",
                                      colour=0xF893B2)
                        embed.set_image(url=url)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await start_embed.delete()
                        await tagname.delete()
                        await tagcontent_embed.delete()
                        return
                    else:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname.content, "content":tagcontent.content})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname.content} \n**Tag's content:** {tagcontent.content}",
                                      colour=0xF893B2)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await start_embed.delete()
                        await tagname.delete()
                        await tagcontent_embed.delete()
                        await tagcontent.delete()
                        return

        if tagname != None and content == None:
            embed = Embed(description=f"Okay! Tag's name is `{tagname}`. Now please provide tag's content, or type `abort` to abort the process.",
                          colour=0xF893B2)
            tagcontent_embed = await ctx.send(embed=embed)
            try:
                tagcontent = await self.bot.wait_for('message', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 1 minute to respond, creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await ctx.message.delete()
                    await tagcontent_embed.delete()
                    return


            cntnt = tagcontent.content
            lowtagcntnt= cntnt.lower()

            if lowtagcntnt == "abort":
                embed = Embed(
                    description=":x: Tag creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await ctx.message.delete()
                await tagcontent_embed.delete()
                await tagcontent.delete()
                return
            else:
                def geturl(string):
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex,string)
                    return [x[0] for x in url]

                if tagcontent.attachments:
                    for url in tagcontent.attachments:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":url.url})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**",
                                      colour=0xF893B2)
                        embed.set_image(url=url.url)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await tagcontent_embed.delete()
                        return
                else:
                    url = geturl(tagcontent.content)
                    for url in url:
                        url = url
                    if url:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":url})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**",
                                      colour=0xF893B2)
                        embed.set_image(url=url)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await tagcontent_embed.delete()
                        return
                    else:
                        table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":tagcontent.content})
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** {tagcontent.content}",
                                      colour=0xF893B2)
                        await ctx.send(embed=embed)
                        await ctx.message.delete()
                        await tagcontent_embed.delete()
                        await tagcontent.delete()
                        return

        if tagname != None and content != None:
            def geturl(string):
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url = re.findall(regex,string)
                return [x[0] for x in url]

            url = geturl(content)
            for url in url:
                url = url
            if url:
                table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":url})
                embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**",
                              colour=0xF893B2)
                embed.set_image(url=url)
                await ctx.send(embed=embed)
                await ctx.message.delete()
                return
            else:
                table.insert_one({"guild_id":ctx.guild.id, "author_id":ctx.message.author.id, "names":tagname, "content":content})
                embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** {content}",
                              colour=0xF893B2)
                await ctx.send(embed=embed)
                await ctx.message.delete()
                return

    @tag.command()
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("tags")
    async def edit(self, ctx, tagname=None, *, content=None):
        """Lets me edit tags."""
        dcluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']

        if tagname == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        tn = table.find({"names":tagname, "guild_id":ctx.guild.id, "author_id":ctx.author.id})
        name = [name.names for name in tn]
        if name == []:
            embed = Embed(description=":x: Couldn't find a tag with that name",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if content == None:
            embed = Embed(
                description=":x: Please provide tag content",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        for t in tn:
            authorid = t.author_id

            if authorid != ctx.author.id:
                embed = Embed(description=":x: You're not the author of this tag, only authors can edit their tags",
                              color=0xDD2222)
                await ctx.send(embed=embed)
                return
            else:
                table.update_one({"names":tagname, "guild_id":ctx.guild.id, "author_id":ctx.author.id}, {"$set":{"content":content}})
                embed = discord.Embed(title="Tag updated",
                                      timestamp=datetime.utcnow(),
                                      colour=0xF893B2)
                embed.add_field(name=f"{tagname}", value=f"{content}", inline=False)
                embed.set_footer(text=f"Author ID:{ctx.author.id}")
                await ctx.send(embed=embed)


    @tag.command()
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("tags")
    async def delete(self, ctx, name=None):
        """Lets me delete tags."""
        if name == None:
            embed = Embed(
                description=":x: Please provide tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']

        names = table.find({"names":name, "guild_id":ctx.guild.id, "author_id":ctx.author.id})
        names = [n['name'] for n in names]
        if names == []:
            embed = Embed(description=f":x: I couldn't find a tag with the name **{name}** that you own.",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        else:
            table.delete_one({"guild_id":ctx.guild.id, "names":name, "author_id":ctx.author.id})
            embed = discord.Embed(title="Tag deleted",
                                  description=f"{name} was deleted by {ctx.author.mention}",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=0xF893B2)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

    @tag.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("tags")
    async def adelete(self, ctx, name=None):
        """[Admin] Delete any tag."""
        if name == None:
            embed = Embed(
                description=":x: Please provide tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']

        names = table.find({"names":name, "guild_id":ctx.guild.id})
        names = [n['name'] for n in names]
        if names == []:
            embed = Embed(description=f":x: I couldn't find a tag with the name **{name}**",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        else:
            table.delete_one({"guild_id":ctx.guild.id, "names":name})
            embed = discord.Embed(title="Tag deleted by an administrator",
                                  description=f"{name} was deleted by {ctx.author.mention}",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=0xF893B2)
            await ctx.send(embed=embed)

    @tag.command()
    @commands.has_permissions(administrator=True)
    @has_active_cogs("tags")
    async def aedit(self, ctx, tagname=None, *, content=None):
        """[Admin] Edit any tag"""
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']

        if tagname == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        tn = table.find({"names":tagname, "guild_id":ctx.guild.id})
        name = [name.names for name in tn]
        if name == []:
            embed = Embed(description=":x: Couldn't find a tag with that name",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if content == None:
            embed = Embed(
                description=":x: Please provide tag content",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        table.update_one({"names":tagname, "guild_id":ctx.guild.id}, {"$set":{"content":content}})
        embed = discord.Embed(title="Tag updated by admin",
                              timestamp=datetime.utcnow(),
                              colour=0xF893B2)
        embed.add_field(name=f"{tagname}", value=f"{content}", inline=False)
        await ctx.send(embed=embed)

    @tag.command()
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("tags")
    async def list(self, ctx):
        """Lists all the tags."""
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

        def newpage(names, guild, pages):
            embed = Embed(description=f"__**List of all the tags for {guild}**__",
            colour=0xF893B2)
            embed.add_field(name="Tag names:", value=f"{names}")
            embed.set_footer(text=pages)
            return embed

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']


        cluster = Mongo.connect()
        db = cluster["giffany"]
        tag_names = db['tag'].find({"guild_id":ctx.guild.id})
        names = [str(name['names'])+"\n" for name in tag_names]

        if names == []:
            embed = Embed(description=f"There are no tags for {ctx.guild}.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1

        nc = list(chunks(names, 20))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
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
                await embedl.edit(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)
        cursor.close()
        db1.close()

    @tag.command(aliases=['i'])
    @has_active_cogs("tags")
    @user_has_role()
    @is_user_blacklisted()
    async def info(self, ctx, *,tagname):
        """Shows you info about the tag."""
        def checkowner(guild, userid):
            members = guild.members
            for m in members:
                if m.id == userid:
                    return m
            return "currently without owner"

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['tag']
        regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tagnames = table.find({"names":regx, "guild_id":ctx.guild.id})
        for tn in tagnames:
            name = tn['names'].lower()

            if tagname.lower() == name:
                owners = table.find({"names":tn['names'], "guild_id":ctx.guild.id})
                tagscontent = table.find({"names":tn['names'], "guild_id":ctx.guild.id})
                for tc in tagscontent:
                    content = tc['content']
                for o in owners:
                    user = await self.bot.fetch_user(o.author_id)
                    if user:
                        user = await self.bot.fetch_user(o.author_id)
                    else:
                        user = f"Not found|{a.author_id}"
                    import regex
                    url = regex.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content.lower())
                    if url:
                        embed = Embed(title=f"Info about {tn['names']}",
                                      colour=0xF893B2)
                        embed.add_field(name="Current owner:", value=f'{checkowner(ctx.guild, o.author_id)}')
                        embed.add_field(name="Last owner:", value=f'{user}')
                        embed.add_field(name="Content:", value="\n\u200b", inline=False)
                        embed.set_image(url=content)
                        async with ctx.typing():
                            await asyncio.sleep(0.3)
                        await ctx.send(embed=embed)
                        return
                    else:
                        embed = Embed(title=f"Info about {tn['names']}",
                                      colour=discord.Colour.from_rgb(59, 136, 195))
                        embed.add_field(name="Current owner:", value=f'{checkowner(ctx.guild, o.author_id)}')
                        embed.add_field(name="Last owner:", value=f'{user}')
                        embed.add_field(name="Content:", value=f"{tc['content']}", inline=False)
                        async with ctx.typing():
                            await asyncio.sleep(0.3)
                        await ctx.send(embed=embed)

        if tagname.lower() != name:
            embed = Embed(
                description=":x: Couldn't find that tag",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

def setup(bot):
    bot.add_cog(Tags(bot))
    print('tags module loaded')
