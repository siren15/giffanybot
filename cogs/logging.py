import discord
import os
import re
import requests
import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
from datetime import datetime, timedelta
from discord import Embed
from discord.ext import commands
from discord.utils import get
from customchecks import *
from motor.motor_asyncio import AsyncIOMotorClient

class Logging(commands.Cog):
    """Guild logging module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['logging'])
    @commands.has_permissions(manage_channels=True)
    @has_active_cogs("logging")
    async def logchannel(self, ctx, channel:discord.TextChannel=None):
        if channel == None:
            embed = Embed(
                description=":x: Please provide a channel",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = await odm.connect()
        channelid = await db.find_one(logs, {"guild_id":ctx.guild.id})
        id = channelid.channel_id
        logchannel = ctx.guild.get_channel(id)
        if logchannel == None:
            table.insert_one({"guild_id":ctx.guild.id, "channel_id":channel.id})
            embed = discord.Embed(description=f"I have assigned {channel.mention} as a log channel.",
                                  color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            table.update_one({"guild_id":ctx.guild.id}, {"$set":{"channel_id":channel.id}})
            embed = discord.Embed(description=f"I have updated {channel.mention} as a log channel.",
                                  color=0xF893B2)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if iscogactive(message.guild, 'logging') == True:
            if is_event_active(message.guild, 'message_deleted'):
                db = await odm.connect()
                channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                id = channelid.channel_id
                log_channel = message.guild.get_channel(id)

                def geturl(string):
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex,string)
                    return [x[0] for x in url]

                if message.attachments:
                    for file in message.attachments:
                        if file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png') or file.filename.endswith('.gif'):
                            url = file.proxy_url
                            if message.content == '':
                                content = "[No written message content]"
                            else:
                                content = message.content

                            embed = discord.Embed(description=f"Message deleted in {message.channel.mention}",
                                                  timestamp=datetime.utcnow(),
                                                  colour=0xfc5f62)
                            embed.set_author(name=message.author)
                            embed.set_thumbnail(url=message.author.avatar_url)
                            embed.add_field(name="Content:", value=f"{content}", inline=False)
                            embed.set_image(url=f"{url}")
                            embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                            await log_channel.send(embed=embed)
                            return
                        else:
                            url = file.proxy_url
                            if message.content == '':
                                content = "[No written message content]"
                            else:
                                content = message.content

                            embed = discord.Embed(description=f"Message deleted in {message.channel.mention}",
                                                  timestamp=datetime.utcnow(),
                                                  colour=0xfc5f62)
                            embed.set_author(name=message.author)
                            embed.set_thumbnail(url=message.author.avatar_url)
                            embed.add_field(name="Content:", value=f"{content}\n\n{url}", inline=False)
                            embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                            await log_channel.send(embed=embed)
                            return
                else:
                    url = geturl(message.content)
                    for url in url:
                        url = url
                    if url:
                        if url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') or url.endswith('.gif'):
                            content = message.content.replace(f'{url}', '')
                            if content == '':
                                content = "[No written message content]"

                            embed = discord.Embed(description=f"Message deleted in {message.channel.mention}",
                                                  timestamp=datetime.utcnow(),
                                                  colour=0xfc5f62)
                            embed.set_author(name=message.author)
                            embed.set_thumbnail(url=message.author.avatar_url)
                            embed.add_field(name="Content:", value=content, inline=False)
                            embed.set_image(url=url)
                            embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                            await log_channel.send(embed=embed)
                            return
                        else:
                            embed = discord.Embed(description=f"Message deleted in {message.channel.mention}",
                                                  timestamp=datetime.utcnow(),
                                                  colour=0xfc5f62)
                            embed.set_author(name=message.author)
                            embed.set_thumbnail(url=message.author.avatar_url)
                            embed.add_field(name="Content:", value=message.content, inline=False)
                            embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                            await log_channel.send(embed=embed)
                            return
                    else:
                        embed = discord.Embed(description=f"Message deleted in {message.channel.mention}",
                                              timestamp=datetime.utcnow(),
                                              colour=0xfc5f62)
                        embed.set_author(name=message.author)
                        embed.set_thumbnail(url=message.author.avatar_url)
                        embed.add_field(name="Content:", value=message.content, inline=False)
                        embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if iscogactive(before.guild, 'logging') == True:
            if is_event_active(before.guild, 'message_edited'):
                db = await odm.connect()
                channelid = await db.find_one(logs, {"guild_id":before.guild.id})
                id = channelid.channel_id
                log_channel = before.guild.get_channel(id)

                if before.content == after.content:
                    return

                embed = discord.Embed(description=f"Message edited in {before.channel.mention}\n[[Jump to message.]]({after.jump_url})",
                                      timestamp=datetime.utcnow(),
                                      colour=0xfcab5f)
                embed.set_author(name=before.author)
                embed.set_thumbnail(url=before.author.avatar_url)
                embed.add_field(name="Original message", value=before.content, inline=False)
                embed.add_field(name="Edited message", value=after.content, inline=False)
                embed.set_footer(text=f'User ID: {before.author.id}\nMessage ID: {before.id}')
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        if iscogactive(member.guild, 'logging') == True:
            if is_event_active(member.guild, 'member_join'):
                db = await odm.connect()
                channelid = await db.find_one(logs, {"guild_id":member.guild.id})
                id = channelid.channel_id
                log_channel = member.guild.get_channel(id)

                d1 = member.created_at
                d2 = datetime.utcnow()
                d = d2 - d1
                d = d.days

                y = (int)(d / 365)
                w = (int)((d % 365) / 7)
                d = (int)(d - ((y * 365) + (w)))

                embed = discord.Embed(description=f"{member.mention}|{member} joined {member.guild}",
                                      timestamp=datetime.utcnow(),
                                      color=0x9af791)
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name="Account age:", value=f"{y}Y {w}W {d}D")
                embed.set_footer(text=f'User ID: {member.id}')
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        if iscogactive(member.guild, 'logging') == True:
            if is_event_active(member.guild, 'member_leave'):
                db = await odm.connect()
                channelid = await db.find_one(logs, {"guild_id":member.guild.id})
                id = channelid.channel_id
                log_channel = member.guild.get_channel(id)

                embed = discord.Embed(description=f"{member.mention}|{member} left {member.guild}",
                                      timestamp=datetime.utcnow(),
                                      color=0xfca85f)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_footer(text=f'User ID: {member.id}')
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        if iscogactive(member.guild, 'logging') == True:
            if is_event_active(member.guild, 'member_kick'):
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                    if entry.target.id == member.id:
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":member.guild.id})
                        id = channelid.channel_id
                        log_channel = member.guild.get_channel(id)

                        embed = discord.Embed(description='{0.user.mention}({0.user}|{0.user.id}) kicked {0.target.mention}|{0.target} | `{0.reason}`'.format(entry),
                                              timestamp=datetime.utcnow(),
                                              color=0xfca85f)
                        embed.set_thumbnail(url=entry.target.avatar_url)
                        embed.set_footer(text=f'User ID: {entry.target.id}')
                        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if iscogactive(guild, 'logging') == True:
            if is_event_active(guild, 'member_ban'):
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    if entry.target.id == user.id:
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":guild.id})
                        id = channelid.channel_id
                        log_channel = member.guild.get_channel(id)

                        embed = discord.Embed(description='{0.user.mention}({0.user}|{0.user.id}) banned {0.target.mention}|{0.target} | `{0.reason}`'.format(entry),
                                              timestamp=datetime.utcnow(),
                                              color=0xfca85f)
                        embed.set_thumbnail(url=entry.target.avatar_url)
                        embed.set_footer(text=f'User ID: {entry.target.id}')
                        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if iscogactive(guild, 'logging') == True:
            if is_event_active(guild, 'member_unban'):
                async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                    if entry.target.id == user.id:
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":guild.id})
                        id = channelid.channel_id
                        log_channel = member.guild.get_channel(id)

                        embed = discord.Embed(description='{0.user.mention}({0.user}|{0.user.id}) unbanned {0.target.mention}|{0.target} | `{0.reason}`'.format(entry),
                                              timestamp=datetime.utcnow(),
                                              color=0xfca85f)
                        embed.set_thumbnail(url=entry.target.avatar_url)
                        embed.set_footer(text=f'User ID: {entry.target.id}')
                        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = before.guild
        if iscogactive(guild, 'logging') == True:
            if is_event_active(before.guild, 'member_roles_update'):
                db = await odm.connect()
                channelid = await db.find_one(logs, {"guild_id":guild.id})
                id = channelid.channel_id
                log_channel = guild.get_channel(id)

                if before.display_name != after.display_name:
                    embed = discord.Embed(description=f"{after.mention} changed their nickname",
                                          timestamp=datetime.utcnow(),
                                          color=0xF893B2)
                    embed.set_thumbnail(url=after.avatar_url)
                    embed.add_field(name="Before", value=before.display_name)
                    embed.add_field(name="After", value=after.display_name)
                    embed.set_footer(text=f'User ID: {before.id}')
                    await log_channel.send(embed=embed)


                new_role = [role for role in after.roles if role not in before.roles]
                old_role = [role for role in before.roles if role not in after.roles]

                r = ''
                for nr in new_role:
                    r = r + f"{nr.mention} "
                    new_role = nr

                o_r = ''
                for o in old_role:
                    o_r = o_r + f"{o.mention} "
                    old_role = o

                if new_role:
                    embed = discord.Embed(description=f"{after.mention} got assigned {r} ",
                                          timestamp=datetime.utcnow(),
                                          color=0xF893B2)
                    embed.set_footer(text=f'User ID: {before.id}')
                    await log_channel.send(embed=embed)

                if old_role:
                    embed = discord.Embed(description=f"{after.mention} was removed from {o_r} ",
                                          timestamp=datetime.utcnow(),
                                          color=0xF893B2)
                    embed.set_footer(text=f'User ID: {before.id}')
                    await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))
    print('logging module loaded')
