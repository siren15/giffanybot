import discord
from discord.ext import commands
from customchecks import *

class ReactionRoles(commands.Cog):
    """reaction roles module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        member = payload.member
        channelid = '191629998027833344'
        channel = self.bot.get_channel(191629998027833344)
        if payload.channel_id == 191629998027833344 and payload.message_id == 860793577587081237:
            if payload.emoji.name == "👍":
                member_roles = [role.name for role in member.roles]
                gfcrole = member.guild.get_role(585208653947207690)
                if 'Gravity Falls Citizens' in member_roles:
                    embed = discord.Embed(description=f"You already agreed to the rules and are a member of `r/GravityFalls` server",
                                  colour=0xF893B2)
                    await member.send(embed=embed)
                    print(f'{member} already is a member of this guild.')
                    return

                elif 'Limbo' in member_roles:
                    embed = discord.Embed(description=f"You can't be let in to `r/GravityFalls` server because you're in Limbo",
                                  colour=0xF893B2)
                    await member.send(embed=embed)
                    print(f'{member} is in limbo, cannot give GFC role to them.')
                    return

                elif 'Muted' in member_roles:
                    embed = discord.Embed(description=f"You can't be let in to `r/GravityFalls` server because you're Muted",
                                  colour=0xF893B2)
                    await member.send(embed=embed)
                    print(f'{member} is muted, cannot give GFC role to them.')
                    return

                else:
                    await member.add_roles(gfcrole)
                    print(f'{member} was given GFC role.')

        #if payload.channel_id == 706376896602177546 and payload.message_id == 717650566062276612:
            #if payload.emoji.name == "shooting_star":
                ##arole = discord.utils.get(payload.member.guild.roles, name='Artists')
                #if arole in member.roles:
                    #await member.remove_roles(arole)
                    #print(f'{member} got removed {arole} role.')
                    #return
                #else:
                    #await member.add_roles(arole)
                    #print(f'{member} was given {arole} role.')

        #if payload.channel_id == 706376896602177546 and payload.message_id == 717650566062276612:
            #if payload.emoji.name == "hello":
                #arole1 = discord.utils.get(payload.member.guild.roles, name='Trainers')
                #if arole1 in member.roles:
                    #await member.remove_roles(arole1)
                    #print(f'{member} got removed {arole1} role.')
                    #return
                #else:
                    #await member.add_roles(arole)
                    #print(f'{member} was given {arole1} role.')

def setup(bot):
    bot.add_cog(ReactionRoles(bot))
    print('reaction roles module loaded')
