#Zephyrus(.GIFfany-testing-grounds)
#Author: @slowmachine#9665
################################
from datetime import datetime
import discord
from mongo import *
import os
import re
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv

###################################
intents = discord.Intents.default()
intents.members = True
messages = joined = 0
###################################
try:
    token = os.environ["zep_token"]
except KeyError:
    token = os.getenv("zep_token")

async def get_prefix(client, message):
    db = await odm.connect()
    prefix = await db.find_one(prefixes, {"guildid":message.guild.id})
    return prefix.prefix

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
#bot.remove_command('help')



@bot.event
async def on_ready():
    print("Zephyrus successfully connected to Discord.")
    print("author:slowmachine#9665")
    await bot.change_presence(activity=discord.Game(name="use z.help for commands"))

@bot.event
async def on_guild_join(guild):
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['prefixes']
    table.insert_one({"guildid":guild.id, "prefix":'z.'})

@bot.event
async def on_guild_remove(guild):
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['prefixes']
    table.delete_one({"guildid":guild.id})

@bot.command(alias=['changeprefix'], description='Changes the prefix of the bot for the guild.')
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix):
    """Changes the prefix of the bot for the guild."""
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['prefixes']
    table.update_one({"guildid":ctx.guild.id}, {"$set":{"prefix":prefix}})
    embed = discord.Embed(title=f"Server prefix changed to: {prefix}",
                          colour=0xF893B2)
    await ctx.send(embed=embed)

##########################################################################
@bot.command(name='botinfo', aliases=['bot', 'info'])
async def botinfo(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=0xF893B2)
    em.title = 'Bot Info'
    em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    try:
        em.description = bot.psa + '\n[Made for r/GravityFalls](https://discord.gg/gravityfalls)'
    except AttributeError:
        em.description = 'A multipurpose bot poorly made by slowmachine#9665\n[Made for r/GravityFalls](https://discord.gg/gravityfalls)'
    em.add_field(name="Servers", value=len(bot.guilds))
    em.add_field(name="Library", value=f"discord.py")
    em.add_field(name="Bot Latency", value=f"{bot.ws.latency * 1000:.0f} ms")
    em.add_field(name='GitHub', value='[Click here](https://github.com/siren15/.GIFfanybot)')
    em.set_footer(text=".GIFfany-bot | Powered by discord.py")
    await ctx.send(embed=em)

#########################################################################
@bot.command(aliases=['activate'])
@commands.has_permissions(administrator=True)
async def enable(ctx, comd=None, *, name=None):
    """Enable bot's features for your guild."""
    modules = ''
    for m in bot.cogs:
        modules = modules + f"{m.lower()},"
    modules = modules.split(',')

    commands = ''
    for c in bot.walk_commands():
        commands = commands + f"{c},"
    commands = commands.split(',')

    events = ['command_not_found', 'welcome_message', 'welcome_card', 'leave_message', 'message_deleted', 'message_edited', 'member_join', 'member_leave', 'member_ban', 'member_kick', 'member_unban', 'member_roles_update']

    evnts = ['listener', 'event', 'listeners', 'events']
    cmds = ['command', 'commands', 'cmd', 'cmds']
    mds = ['module', 'modules', 'cog', 'cogs']

    if comd is None:
        embed = Embed(
            description=":x: Please provide what kind of feature you want to enable [command/module/event]",
            color=0xDD2222)
        await ctx.send(embed=embed)
        return

    if comd.lower() in evnts:
        if name == None:
            embed = Embed(
                description=":x: Please provide a name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in events:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            commands = table.find({"guildid":ctx.guild.id})
            activecommands = ''
            for c in commands:
                activecommands = activecommands + f"0, {c['activecommands'].lower()}"
                if name.lower() in activecommands:
                    embed = Embed(
                        description=f":x: **{name}** is already enabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecommands == "0, ":
                    names = name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
                else:
                    names = c['activecommands'] + name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

    if comd in cmds:
        if name == None:
            embed = Embed(
                description=":x: Please provide a name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in commands:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            commands = table.find({"guildid":ctx.guild.id})
            activecommands = ''
            for c in commands:
                activecommands = activecommands + f"0, {c['activecommands'].lower()}"
                if name.lower() in activecommands:
                    embed = Embed(
                        description=f":x: **{name}** is already enabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecommands == "0, ":
                    names = name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
                else:
                    names = c['activecommands'] + name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

    if comd in mds:
        if name == None:
            embed = Embed(
                description=":x: Please provide a module name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in modules:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            cogs = table.find({"guildid":ctx.guild.id})
            activecogs= ''
            for c in cogs:
                activecogs = activecogs + f"0, {c['activecogs'].lower()}"
                if name.lower() in activecogs:
                    embed = Embed(
                        description=f":x: **{name}** module is already enabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecogs == "0, ":
                    names = name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecogs":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** module has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
                else:
                    names = c['activecogs'] + name.lower()
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecogs":f"{names},"}})
                    embed = Embed(
                        description=f"**{name}** module has been successfully enabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)

@bot.command(aliases=['deactivate'])
@commands.has_permissions(administrator=True)
async def disable(ctx, comd=None, *, name=None):
    """Disable bot's features for your guild."""
    modules = ''
    for m in bot.cogs:
        modules = modules + f"{m.lower()},"
    modules = modules.split(',')

    commands = ''
    for c in bot.walk_commands():
        commands = commands + f"{c},"
    commands = commands.split(',')

    events = ['command_not_found','welcome_message', 'welcome_card', 'leave_message', 'message_deleted', 'message_edited', 'member_join', 'member_leave', 'member_ban', 'member_kick', 'member_unban', 'member_roles_update']

    evnts = ['listener', 'event', 'listeners', 'events']
    cmds = ['command', 'commands', 'cmd', 'cmds']
    mds = ['module', 'modules', 'cog', 'cogs']

    if comd is None:
        embed = Embed(
            description=":x: Please provide what kind of feature you want to disable [command/module/event]",
            color=0xDD2222)
        await ctx.send(embed=embed)
        return

    if comd.lower() in evnts:
        if name == None:
            embed = Embed(
                description=":x: Please provide a name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in events:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            commands = table.find({"guildid":ctx.guild.id})
            activecommands = ''
            for c in commands:
                activecommands = activecommands + f"0, {c['activecommands'].lower()}"
                if name.lower() not in activecommands:
                    embed = Embed(
                        description=f":x: **{name}** is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecommands == "0, ":
                    embed = Embed(
                        description=f":x: **{name}** is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                else:
                    namel = name.lower() + ","
                    names = c['activecommands'].replace(namel, '')
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":names}})
                    embed = Embed(
                        description=f"**{name}** has been successfully disabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)

    if comd.lower() in cmds:
        if name == None:
            embed = Embed(
                description=":x: Please provide a name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in commands:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            commands = table.find({"guildid":ctx.guild.id})
            activecommands = ''
            for c in commands:
                activecommands = activecommands + f"0, {c['activecommands'].lower()}"
                if name.lower() not in activecommands:
                    embed = Embed(
                        description=f":x: **{name}** is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecommands == "0, ":
                    embed = Embed(
                        description=f":x: **{name}** is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                else:
                    namel = name.lower() + ","
                    names = c['activecommands'].replace(namel, '')
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecommands":names}})
                    embed = Embed(
                        description=f"**{name}** has been successfully disabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)

    elif comd.lower() in mds:
        if name == None:
            embed = Embed(
                description=":x: Please provide a module name.",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if name.lower() in modules:
            cluster = Mongo.connect()
            db = cluster["giffany"]
            table = db['prefixes']
            cogs = table.find({"guildid":ctx.guild.id})
            activecogs= ''
            for c in cogs:
                activecogs = activecogs + f"0, {c['activecogs'].lower()}"
                if name.lower() not in activecogs:
                    embed = Embed(
                        description=f":x: **{name}** module is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if activecogs == "0, ":
                    embed = Embed(
                        description=f":x: **{name}** module is already disabled",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                else:
                    namel = name.lower() + ","
                    names = c['activecogs'].replace(namel, '')
                    table.update_one({"guildid":ctx.guild.id}, {"$set":{"activecogs":names}})
                    embed = Embed(
                        description=f"**{name}** module has been successfully disabled.",
                        color=0xF893B2)
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: **{name}** is not recognized",
                color=0xDD2222)
            await ctx.send(embed=embed)
@bot.command(aliases=['restrictcmd', 'rcmd'])
@commands.has_permissions(administrator=True)
async def restrictcommand(ctx, cmd_name=None, *, role:discord.Role=None):
    if role == None:
        embed = Embed(
            description=f":x: Please provide a role",
            color=0xDD2222)
        await ctx.send(embed=embed)
    if cmd_name == None:
        embed = Embed(
            description=f":x: Please provide a command name",
            color=0xDD2222)
        await ctx.send(embed=embed)

    commands = [c.qualified_name for c in bot.walk_commands()]

    def gn(guild, cmd_name):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['hasrole']
        regx = re.compile(f"^{cmd_name}$", re.IGNORECASE)
        roleid = table.find({"guildid":guild.id, "command":regx})
        for role in roleid:
            return role['command']
        return None
    if cmd_name.lower() in commands:
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['hasrole']
        cmd = gn(ctx.guild, cmd_name)
        if cmd == None:
            table.insert_one({"guildid":ctx.guild.id, "command":cmd_name, "role":role.id})
            embed = Embed(
                description=f"**{cmd_name}** has been successfully restricted to {role.mention}",
                color=0xF893B2)
            await ctx.send(embed=embed)
        else:
            table.update_one({"guildid":ctx.guild.id, "command":cmd_name}, {"$set":{"role":role.id}})
            embed = Embed(
                description=f"**{cmd_name}** commands restriction has been updated to {role.mention}",
                color=0xF893B2)
            await ctx.send(embed=embed)
    else:
        embed = Embed(
            description=f":x: **{cmd_name}** is not a command",
            color=0xDD2222)
        await ctx.send(embed=embed)

@bot.command(aliases=['restrictremove', 'restrictdel', 'resdel'])
@commands.has_permissions(administrator=True)
async def restrictdelete(ctx, *, cmd_name):
    if cmd_name == None:
        embed = Embed(
            description=f":x: Please provide a command name",
            color=0xDD2222)
        await ctx.send(embed=embed)
    def gn(guild, cmd_name):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['hasrole']
        regx = re.compile(f"^{cmd_name}$", re.IGNORECASE)
        roleid = table.find({"guildid":guild.id, "command":regx})
        for role in roleid:
            return role['command']
        return None
    cluster = Mongo.connect()
    db = cluster["giffany"]
    table = db['hasrole']
    cmd = gn(ctx.guild, cmd_name)
    if cmd == None:
        embed = Embed(
            description=f":x: **{cmd_name}** doesn't have any role restrictions",
            color=0xDD2222)
        await ctx.send(embed=embed)
    else:
        table.delete_one({"guildid":ctx.guild.id, "command":cmd_name})
        embed = Embed(
            description=f"**{cmd_name}** command restriction has been removed",
            color=0xF893B2)
        await ctx.send(embed=embed)
##########################################################################
@bot.command()
@commands.is_owner()
async def botdisable(ctx, name):
    await bot.remove_command(name)
    embed = discord.Embed(description=" Disabled {0}".format(name),
                          timestamp=datetime.utcnow(),
                          color=0xF893B2)
    await ctx.send(embed=embed)

##########################################################################
@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    print(f"{extension} reloaded")
    embed = discord.Embed(description=" Reloaded {0}".format(extension),
                          timestamp=datetime.utcnow(),
                          color=0xF893B2)
    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    embed = discord.Embed(description=" Loaded {0}".format(extension),
                          timestamp=datetime.utcnow(),
                          color=0xF893B2)
    await ctx.send(embed=embed)
    print(f"loaded {extension}")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    embed = discord.Embed(description=" Unloaded {0}".format(extension),
                          timestamp=datetime.utcnow(),
                          color=0xF893B2)
    await ctx.send(embed=embed)
    print(f"unloaded {extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
