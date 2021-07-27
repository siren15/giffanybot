import discord

from datetime import datetime, timedelta
from discord import Embed
from discord.ext import commands
from discord.utils import get
from stuf import stuf
from customchecks import *
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model



class OnError(commands.Cog):
    """banning the ducks"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        def chids(guild):
            cluster = Mongo.connect()
            db = cluster["giffany"]
            channelids = db['logs'].find({"guild_id":guild.id})
            for channel in channelids:
                id = channel['channel_id']
                return id
            return None

        log_ch_from_db = chids(member.guild)
        log_channel = member.guild.get_channel(int(log_ch_from_db))
        if member.name.lower() == 'aixal-20' and member.guild.id == 149167686159564800:
            def random_string_generator():
                characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
                result=''
                for i in range(0, 8):
                    result += random.choice(characters)
                return result

            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['strikes']

            stid = True
            while stid == True:
                sid = random_string_generator()
                dbsid = db['strikes'].find({"strikeid":sid})
                dbsid = [s['strikeid'] for s in dbsid]
                if dbsid != sid:
                    stid = False
                else:
                    stid == True

            daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
            table.insert_one({"strikeid":sid, "guildid":member.guild.id, "user":member.id, "moderator":'automod duckbanner system', "action":"Ban", "day":daytime, "reason":'being a duck :MabelKek:'})

            embed = Embed(description=f":grey_exclamation: **You have been banned in {member.guild} for:** being an asshole with a lot of alts",
                          colour=0xF893B2)
            embed.set_image(url='https://cdn.discordapp.com/attachments/604071095280336947/830872034350596166/ezgif.com-gif-maker1.gif')
            await member.send(embed=embed)
            await member.guild.ban(discord.Object(id=int(member.id)), reason='being a duck :MabelKek:(aixal alt)', delete_message_days=0)
            embed = discord.Embed(description=f"{member} was banned \n**Member ID:** {member.id} \nReason: being a duck :MabelKek: \n**Actioned by:** automod duckbanner system",
                                  colour=0xF893B2,
                                  timestamp=datetime.utcnow())
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_image(url='https://cdn.discordapp.com/attachments/604071095280336947/830872034350596166/ezgif.com-gif-maker1.gif')
            await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(OnError(bot))
    print('duckbanner module loaded')
