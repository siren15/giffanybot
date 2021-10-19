import discord
from mongo import *
from discord import Embed
from datetime import datetime
from discord.ext import commands
from customchecks import *
import requests
import random
from urllib.parse import urlparse

class scambotfilter(commands.Cog):
    """scambot filter"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author == self.bot.user) or (message.author.id == 650041398535389206):
            return

        def geturl(string):
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            url = re.findall(regex,string)
            return [x[0] for x in url]

        def random_string_generator():
            characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
            result=''
            for i in range(0, 8):
                result += random.choice(characters)
            return result

        url = geturl(message.content)
        for url in url:
            url = url

        url = urlparse(url).netloc
        if 'www.' in str(url):
            url = url.replace('www.','')

        scam_links = requests.get('https://api.hyperphish.com/gimme-domains').content
        scam_links = scam_links.decode("UTF-8").replace("[",'')
        scam_links = scam_links.replace("]", '')
        scam_links = scam_links.replace('"','')
        scam_links = scam_links.split(',')

        is_scam = False

        if url in scam_links:
            is_scam = True

        elif ("@everyone" in message.content) and ("nitro" in message.content):
            is_scam = True

        if is_scam == True:
            await message.delete()
            await message.author.kick(reason="[automod]nitro scambot")

            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['strikes']
            while True:
                sid = random_string_generator()
                dbid = [i['strikeid'] for i in db['strikes'].find({"strikeid":sid})]
                if dbid == []:
                    break
                for i in dbid:
                    if i == sid:
                        continue
                    else:
                        break

            daytime = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
            table.insert_one({"strikeid":sid, "guildid":message.guild.id, "user":message.author.id, "moderator":"[automod]", "action":"Kick", "day":daytime, "reason":"[automod]nitro scambot"})

            embed = Embed(colour=0xF893B2,
                          timestamp=datetime.utcnow())
            embed.set_author(name=f"{message.author} has been kicked| [automod]nitro scambot", icon_url=message.author.avatar_url)
            embed.set_footer(text=f'Member ID: {message.author.id}')
            db = await odm.connect()
            channelid = await db.find_one(logs, {"guild_id":message.guild.id})
            id = channelid.channel_id
            log_channel = message.guild.get_channel(id)
            await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(scambotfilter(bot))
    print('scambot filter module loaded')
