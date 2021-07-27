from datetime import datetime
from random import choice, randint
from typing import Optional
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import dataset
import discord
from aiohttp import request
from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument, CheckFailure
from discord.ext.commands import command, cooldown
from customchecks import *

class Fun(commands.Cog):
    """All the fun commands."""
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"])
    @cooldown(3, 60, BucketType.guild)
    @has_active_cogs("Fun")
    @is_user_blacklisted()
    async def say_hello(self, ctx):
        """Say hello to .GIFfany"""
        messages = ["Hello",
                    "Hi",
                    "Hey",
                    "I am sure you'll never abandon me, new boyfriend",
                    "https://cdn.discordapp.com/attachments/604071095280336947/804772581201805372/giffany-pissed.gif"]
        await ctx.send(choice(messages) + ctx.author.mention)

    @commands.command(aliases=["hit", 'punch'])
    @cooldown(3, 60, BucketType.guild)
    @user_has_role()
    @is_user_blacklisted()
    @has_active_cogs("Fun")
    async def slap(self, ctx, member: discord.Member=None, *, reason: Optional[str] = "no reason"):
        """Slapity slap. Slap your mortal enemy."""
        slaps = ['https://i.pinimg.com/originals/68/de/67/68de679cc20000570e8a7d9ed9218cd3.gif',
                 'https://external-preview.redd.it/9Bli5uijJkmSuZ6CFIVtnqfyeZt3tc4ghpg5jCuuqaE.gif?width=500&s=ee57ca181800acad72dd6eb47ed81b50b88d1f89',
                 'https://gifimage.net/wp-content/uploads/2017/07/anime-slap-gif-12.gif',
                 'https://media1.tenor.com/images/0860d681fbe7ad04a2f39735ab939176/tenor.gif?itemid=13642334',
                 'https://media1.tenor.com/images/af36628688f5f50f297c5e4bce61a35c/tenor.gif?itemid=17314633',
                 'https://media1.tenor.com/images/1cf84bf514d2abd2810588caf7d9fd08/tenor.gif?itemid=7679403',
                 'http://i1224.photobucket.com/albums/ee365/TehKL/_anime_doubleslap.gif',
                 'https://68.media.tumblr.com/4be8a45a0d67ded0c5d7192738d2d104/tumblr_o7gh4lSewD1upfgqvo1_500.gif',
                 'https://gifimage.net/wp-content/uploads/2017/07/anime-slap-gif-10.gif',
                 'https://25.media.tumblr.com/3910dcc83498c9bed52ff474d37540ce/tumblr_mjtddrGIur1s3jnxpo2_500.gif',
                 'https://i.pinimg.com/originals/95/c4/7e/95c47e29bb9785cffc9789946d717619.gif',
                 'https://media1.tenor.com/images/358986720d4b533a49bdb67cbc4fe3e5/tenor.gif?itemid=14179582',
                 'https://i.pinimg.com/originals/a0/dc/ce/a0dcce4e6eda2eba39d9f1fca82d32b6.gif',
                 'https://i0.kym-cdn.com/photos/images/original/001/276/444/aee.gif',
                 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/845bb266-6572-43ef-8978-d33447959ab1/d5j34yz-8f59a703-c836-4be5-bfda-44089b843b27.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi84NDViYjI2Ni02NTcyLTQzZWYtODk3OC1kMzM0NDc5NTlhYjEvZDVqMzR5ei04ZjU5YTcwMy1jODM2LTRiZTUtYmZkYS00NDA4OWI4NDNiMjcuZ2lmIn1dXX0.52Vxirsu9OM5n8O6-f0egIrNpQMZcqQOVAG5bNDwGao',
                 'https://media.tenor.com/images/e7ed58b227d4787a2b55f00d55fa730a/tenor.gif',
                 'https://media.tenor.com/images/cdb9a6b7fa6572c259ac5b76f98685d4/tenor.gif',
                 'https://media.tenor.com/images/b6f4b0267c09e58ccf2e17b925409968/tenor.gif',
                 'https://media.tenor.com/images/a93096c2fff6e5759d5ad0517f3cdbc5/tenor.gif',
                 'https://media.tenor.com/images/cfba82d1adca7fc73566d04f1b3bf17b/tenor.gif'

        ]

        if member is None:
            member = ctx.message.author
            embed = discord.Embed(
                description=f"{ctx.author.mention} slapped {member.mention} for {reason}! Stop hitting yourself!",
                colour=ctx.author.top_role.colour)
            embed.set_image(url=choice(slaps))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"{ctx.author.mention} slapped {member.mention} for {reason}!",
                colour=ctx.author.top_role.colour)
            embed.set_image(url=choice(slaps))
            await ctx.send(embed=embed)

    @commands.command(aliases=['fban', 'yeet'])
    @has_active_cogs("Fun")
    @user_has_role()
    @is_user_blacklisted()
    async def fakeban(self, ctx, member: discord.Member = None, *, reason=None):
        """Fake ban member from guild. Use: .tag ban <member(s)> <reason>"""
        if member == ctx.message.author:
            embed = Embed(
                description=":x: You cannot ban yourself!",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == None:
            embed = Embed(
                description=":x: Please provide a a user!",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if reason == None:
            reason = "No reason provided."
        embed = discord.Embed(description=f"{member.mention} was yeeted from {ctx.guild} for {reason} by {ctx.author.mention}", colour=discord.Colour.from_rgb(119, 178, 85))
        embed.set_image(url='https://i.imgur.com/V4tZBCK.gif')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
    print('fun module loaded')
