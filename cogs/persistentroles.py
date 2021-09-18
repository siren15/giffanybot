from mongo import *
import discord
import re
from discord.ext import commands
from customchecks import *
from discord.utils import get

class persistent_roles(commands.Cog):
    """Makes roles persistent when members leave, and will give them back when they rejoin."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_roles = [role for role in member.roles if role.name != '@everyone']
        rolecount = len(member_roles)
        if rolecount == 0:
            return
        else:
            db = await odm.connect()
            check = await db.find_one(persistentroles, {"guildid":member.guild.id, "userid":member.id})
            if check == None:
                member_roles = ",".join([str(role.id) for role in member.roles if role.name != '@everyone'])
                await db.save(persistentroles(guildid=member.guild.id, userid=member.id, roles=member_roles))
            else:
                db.delete(check)
                member_roles = ",".join([str(role.id) for role in member.roles if role.name != '@everyone'])
                await db.save(persistentroles(guildid=member.guild.id, userid=member.id, roles=member_roles))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await odm.connect()
        u = await db.find_one(persistentroles, {"guildid":member.guild.id, "userid":member.id})
        if member.id == u.userid:
            roles = [u.roles.split(',')]
            for roles in roles:
                roles = [member.guild.get_role(int(id_)) for id_ in roles if len(id_)]
                roles = roles + member.roles
                await member.edit(roles=roles)
                db.delete(user)

def setup(bot):
    bot.add_cog(persistent_roles(bot))
    print('persistent roles module loaded')
