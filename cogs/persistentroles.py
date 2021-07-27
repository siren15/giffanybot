import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import discord
from discord.ext import commands
from customchecks import *
from discord.utils import get

class persistentroles(commands.Cog):
    """Makes roles persistent when members leave, and will give them back when they rejoin."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            await member.guild.fetch_ban(member)
        except discord.NotFound:
            member_roles = [role for role in member.roles if role.name != '@everyone']
            rolecount = len(member_roles)
            if rolecount == 0:
                return
            else:
                cluster = Mongo.connect()
                db = cluster["giffany"]
                member_roles = ",".join([str(role.id) for role in member.roles if role.name != '@everyone'])
                user = db['persistentroles'].find({"guildid":member.guild.id, "userid":member.id})
                for u in user:
                    if u['userid'] == member.id:
                        db['persistentroles'].delete_one({"guildid":member.guild.id, "userid":member.id})
                        db['persistentroles'].insert_one({"guildid":member.guild.id, "userid":member.id, "roles":member_roles})
                    else:
                        db['persistentroles'].insert_one({"guildid":member.guild.id, "userid":member.id, "roles":member_roles})
        else:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['persistentroles']
        users = table.find({"guildid":member.guild.id, "userid":member.id})
        for user in users:
            if member.id == user['userid']:
                roles = table.find({"guildid":member.guild.id, "userid":member.id})
                roles = [r['roles'].split(',') for r in roles]
                for roles in roles:
                    roles = [member.guild.get_role(int(id_)) for id_ in roles if len(id_)]
                    roles = roles + member.roles
                    await member.edit(roles=roles)
                    table.delete_one({"guildid":member.guild.id, "userid":member.id})

def setup(bot):
    bot.add_cog(persistentroles(bot))
    print('persistent roles module loaded')
