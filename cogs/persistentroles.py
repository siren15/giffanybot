import pymongo
from pymongo import MongoClient
from mongo import *
from odmantic import AIOEngine
from typing import Optional
from odmantic import Field, Model
import discord
import re
from discord.ext import commands
from customchecks import *
from discord.utils import get

class persistentroles(commands.Cog):
    """Makes roles persistent when members leave, and will give them back when they rejoin."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                return
        try:
            await member.guild.fetch_ban(member)
        except discord.NotFound:
            member_roles = [role for role in member.roles if role.name != '@everyone']
            rolecount = len(member_roles)
            if rolecount == 0:
                return
            else:
                db = await odm.connect()
                check = await db.find_one(persistentroles, {"guildid":member.guild.id, "userid":member.id})
                if check == None:
                    db.delete(check)
                
                member_roles = ",".join([str(role.id) for role in member.roles if role.name != '@everyone'])
                await db.save(persistentroles, {"guildid":member.guild.id, "userid":member.id, "roles":member_roles})
        else:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await odm.connect()
        users = await db.find_one(persistentroles, {"guildid":member.guild.id, "userid":member.id})
        if member.id == users.userid:
            r = await db.find_one(persistentroles, {"guildid":member.guild.id, "userid":member.id})
            roles = [r.roles.split(',')]
            for roles in roles:
                roles = [member.guild.get_role(int(id_)) for id_ in roles if len(id_)]
                roles = roles + member.roles
                await member.edit(roles=roles)
                await db.delete(r)

def setup(bot):
    bot.add_cog(persistentroles(bot))
    print('persistent roles module loaded')
