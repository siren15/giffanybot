import discord
import hashlib
import os
import requests
from discord.ext import commands
from customchecks import *

def download(url):
    video = requests.get(url)
    with open("video.mp4",'wb') as afile:
        afile.write(video.content)
        afile.close()

class crashfilter(commands.Cog):
    """Chat exporter module."""
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    @has_active_cogs("crashfilter")
    async def on_message(self, message):
        hashes = ['35bd9b15a6768346cbb372b4a6e6a8c1',
                  'e76d45de590fde52d96ec80aa316aa6b',
                  'b00cae47c8f8aece79a77d51599e072e',
                  'cf57130cb33db6d7c00742225ff98ed4',
                  '8b2da0eef8745675425874fe66e779d7'

        ]
        if message.attachments and isguild(message.guild, 149167686159564800) == True:
            for filename in message.attachments:
                if '.mp4' in filename.filename:
                    await filename.save(filename.filename)
                    hasher = hashlib.md5()
                    with open(f'{filename.filename}', 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    for h in hashes:
                        if hasher.hexdigest() in h:
                            await message.delete()
                            embed = discord.Embed(
                                description=f":x: {message.author.mention} Woah there buddy, we don't allow these 'discord crash' videos here.",
                                color=0xDD2222)
                            await message.channel.send(embed=embed)
                            print(f"{message.author} sent crash video: {filename.filename}")
                            os.remove(filename.filename)
                            return
                        if hasher.hexdigest() not in h:
                            os.remove(filename.filename)
                            return

        if 'https://' and '.mp4' in message.content and isguild(message.guild, 149167686159564800) == True:
            msg = message.content.split(" ")
            for url in msg:
                if url.startswith('https://') and url.endswith('.mp4'):
                    download(url)
                    hasher = hashlib.md5()
                    with open(f'video.mp4', 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    for h in hashes:
                        if hasher.hexdigest() in h:
                            await message.delete()
                            embed = discord.Embed(
                                description=f":x: {message.author.mention} Woah there buddy, we don't allow these 'discord crash' videos here.",
                                color=0xDD2222)
                            await message.channel.send(embed=embed)
                            print(f"{message.author} sent crash video: {url}")
                            os.remove('video.mp4')

def setup(bot):
    bot.add_cog(crashfilter(bot))
    print('crashfilter module loaded')
