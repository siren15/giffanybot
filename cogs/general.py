import os
import dataset
import discord
from datetime import datetime
from discord import Embed
from discord.ext import commands
from discord.ext.commands import BucketType
from customchecks import *

def howlong(date):
    d = (datetime.utcnow() - date).days

    y = (int)(d / 365)
    w = (int)((d % 365) / 7)
    d = (int)(d - ((y * 365) + (w)))
    return f"{y}Y {w}W {d}D"

class General(commands.Cog):
    """General use commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["userinfo", "whodat", "i"])
    async def whois(self, ctx, member: discord.Member = None):
        """Shows you the current information about a member. If member is not provided it will instead show your information. Use: .whois <member> Aliases:userinfo"""
        if member == None:
            member = ctx.message.author

        if member.top_role.name != '@everyone':
            toprole = member.top_role.mention
        else:
            toprole = 'None'

        roles = [role.mention for role in member.roles if role.name != '@everyone']
        rolecount = len(roles)
        if rolecount == 0:
            roles = 'None'
        else:
            roles = ' '.join(roles)

        if member.top_role.colour.value == 0:
            colour = 0xF893B2
        else:
            colour = member.top_role.colour
        embed = discord.Embed(colour=colour,
                              timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="ID(snowflake):", value=member.id, inline=False)
        embed.add_field(name="Nickname:", value=member.display_name, inline=False)
        embed.add_field(name="Created account on:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{howlong(member.created_at)}]", inline=False)
        embed.add_field(name="Joined server on:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{howlong(member.joined_at)}]", inline=False)
        embed.add_field(name=f"Roles: [{rolecount}]", value=roles, inline=False)
        embed.add_field(name="Highest role:", value=toprole, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["whatsdat"])
    async def serverinfo(self, ctx):
        """Shows you the current information about the server. Aliases:whatsdat"""
        guild = ctx.guild
        embed = discord.Embed(title=f"Server Info", colour=0xF893B2)
        embed.set_author(name=f'{guild.name}', icon_url=f'{guild.icon_url}')
        embed.set_thumbnail(url=f'{guild.icon_url}')
        embed.add_field(name='Server owner', value=f'{guild.owner.mention}', inline=False)
        embed.add_field(name='Members', value=f'{guild.member_count}', inline=False)
        embed.add_field(name="Channels:", value=len(guild.channels), inline=False)
        embed.add_field(name="Roles:", value=len(guild.roles), inline=False)
        embed.add_field(name='Boost level', value=f'{guild.premium_tier}', inline=False)
        embed.add_field(name='Created at', value=f'{guild.created_at} [{howlong(guild.created_at)}]', inline=False)
        embed.add_field(name='Region', value=f'{guild.region}', inline=False)
        embed.add_field(name='ID', value=f'{guild.id}', inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["pfp"])
    @commands.cooldown(1, 15, BucketType.guild)
    @has_active_cogs("general")
    @user_has_role()
    @is_user_blacklisted()
    async def avatar(self, ctx, member: discord.Member = None):
        """Shows you your avatar, or members avatar if member is provided. Use: .avatar <member>"""
        if member == None:
            member = ctx.message.author
            filename = f"{member}.gif"
            await ctx.author.avatar_url.save(filename)
            file = discord.File(fp=filename)
            await ctx.send("Enjoy :>", file=file)
            filepath = './{0}'.format(filename)
            os.remove(filepath)
        else:
            filename = f"{member}.gif"
            await member.avatar_url.save(filename)
            file = discord.File(fp=filename)
            await ctx.send("Enjoy :>", file=file)
            os.remove(filename)

    @commands.command(aliases=["say"])
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx, *, message):
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx):
        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author == ctx.message.author

        embed = discord.Embed(
            description="Embed creation started. I will save your next message as the embed title, or type `abort` to abort the process.",
            colour=discord.Colour.from_rgb(59, 136, 195))
        startembed = await ctx.send(embed=embed)


        try:
            name = await self.bot.wait_for('message', timeout=90.0, check=check)

        except asyncio.TimeoutError:
                embed = Embed(
                    description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, embed creation cancelled.",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await startembed.delete()
                await ctx.message.delete()
                return

        cntnt = name.content
        content = cntnt.lower()

        if content == "abort":
            embed = Embed(
                description=":x: Embed creation process aborted",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await startembed.delete()
            await name.delete()
            await ctx.message.delete()
            return

        else:
            embed = Embed(
                description=f"Embed's title is `{name.content}`. Now please provide embed content. I will save your next message as the embed content, or type `abort` to abort the process.",
                colour=discord.Colour.from_rgb(59, 136, 195))
            msgembed = await ctx.send(embed=embed)
            try:
                contentmsg = await self.bot.wait_for('message', timeout=90.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, embed creation cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await startembed.delete()
                    await name.delete()
                    await msgembed.delete()
                    await ctx.message.delete()

            cntnt = contentmsg.content
            content = cntnt.lower()

            if content == "abort":
                embed = Embed(
                    description=":x: Embed creation process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await startembed.delete()
                await name.delete()
                await msgembed.delete()
                await contentmsg.delete()
                await ctx.message.delete()
                return
            else:
                embed = Embed(title=name.content,
                              description=cntnt,
                              colour=0xF893B2)
                await ctx.send(embed=embed)
                await startembed.delete()
                await name.delete()
                await msgembed.delete()
                await contentmsg.delete()
                await ctx.message.delete()
                return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def editembed(self, ctx, embedid):
        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author == ctx.message.author

        embed = discord.Embed(
            description="Embed edit started. I will save your next message as the embed title, or type `abort` to abort the process.",
            colour=discord.Colour.from_rgb(59, 136, 195))
        startembed = await ctx.send(embed=embed)

        try:
            name = await self.bot.wait_for('message', timeout=90.0, check=check)

        except asyncio.TimeoutError:
                embed = Embed(
                    description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, embed edit cancelled.",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await startembed.delete()
                await ctx.message.delete()
                return

        cntnt = name.content
        content = cntnt.lower()

        if content == "abort":
            embed = Embed(
                description=":x: Embed edit process aborted",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await startembed.delete()
            await name.delete()
            await ctx.message.delete()
            return

        else:
            embed = Embed(
                description=f"Embed's title is `{name.content}`. Now please provide embed content. I will save your next message as the embed content, or type `abort` to abort the process.",
                colour=discord.Colour.from_rgb(59, 136, 195))
            msgembed = await ctx.send(embed=embed)
            try:
                contentmsg = await self.bot.wait_for('message', timeout=90.0, check=check)

            except asyncio.TimeoutError:
                    embed = Embed(
                        description=f":x: Uh oh, {ctx.message.author.mention}! You took longer than 2 minutes to respond, embed edit cancelled.",
                        color=0xDD2222)
                    await ctx.channel.send(embed=embed)
                    await startembed.delete()
                    await name.delete()
                    await msgembed.delete()
                    await ctx.message.delete()

            cntnt = contentmsg.content
            content = cntnt.lower()

            if content == "abort":
                embed = Embed(
                    description=":x: Embed edit process aborted",
                    color=0xDD2222)
                await ctx.channel.send(embed=embed)
                await startembed.delete()
                await name.delete()
                await msgembed.delete()
                await contentmsg.delete()
                await ctx.message.delete()
                return
            else:
                oldembed = await ctx.fetch_message(embedid)
                editembed = Embed(title=name.content,
                              description=contentmsg.content,
                              colour=0xF893B2)
                await oldembed.edit(embed=editembed)
                await startembed.delete()
                await name.delete()
                await msgembed.delete()
                await contentmsg.delete()
                await ctx.message.delete()
                return

def setup(bot):
    bot.add_cog(General(bot))
    print('general module loaded')
