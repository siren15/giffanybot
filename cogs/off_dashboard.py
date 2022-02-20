from datetime import datetime
import discord
import re
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
        pass

def setup(bot):
    bot.add_cog(dashboard(bot))
    print('dashboard module loaded')
