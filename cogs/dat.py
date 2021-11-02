import discord
from mongo import *
from discord import Embed
from discord.ext import commands
from customchecks import *

class dat(commands.Cog):
    """draw-a-thon submittion system"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Gravity Falls Citizens')
    async def submit(self, ctx, *, prompt=None):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['dat']
        prompt_list = ['wandering',
                       'trail',
                       'fall',
                       'deep',
                       'crooked',
                       'screech',
                       'a closet',
                       'closet',
                       'at the foot of a hill',
                       'sin',
                       'odor',
                       'scar',
                       'shattered',
                       'run',
                       'florescent',
                       'playground',
                       'halloween']
        if prompt == None:
            embed = Embed(
                description=f":x: {ctx.author.mention} Please provide a prompt you're submitting for",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return

        elif prompt.lower() not in prompt_list:
            embed = Embed(
                description=f":x: {ctx.author.mention} Please provide a correct prompt from our prompt list",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return

        elif prompt.lower() in prompt_list:
            regx = re.compile(f"^{prompt}$", re.IGNORECASE)
            check = table.find_one({"authorid":ctx.author.id, "prompts":regx, "guildid":ctx.guild.id})
            print(check)
            if check == None:
                if ctx.message.attachments:
                    for url in ctx.message.attachments:
                        table.insert_one({"guildid":ctx.guild.id, "authorid":ctx.message.author.id, "prompts":prompt, "content":url.url, 'resubmitted':False})
                        embed = Embed(description=f"{ctx.author.mention} __**Submitted!**__ \n**Prompt:** {prompt} \n**Tag's content: {url.url}**",
                                      colour=0xF893B2)
                        await ctx.send(embed=embed)
                        return
                else:
                    embed = Embed(
                        description=f":x: {ctx.author.mention} Please upload a drawing you're submitting for together with the command like this:",
                        color=0xDD2222)
                    embed.set_image(url='https://i.imgur.com/tqW93GO.png')
                    await ctx.send(embed=embed)
                    await ctx.message.delete()
                    return

            if check['prompts'] == prompt.lower():
                embed = Embed(
                    description=f":x: {ctx.author.mention} You already submitted for this prompt already, if you want to resubmit you can one time for each prompt using .resubmit 'prompt name' with uploading the correct drawing in one message",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await ctx.message.delete()
                return



    @commands.command()
    async def resubmit(self, ctx, *, prompt=None):
        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['dat']
        prompt_list = ['wandering',
                       'trail',
                       'fall',
                       'deep',
                       'crooked',
                       'screech',
                       'a closet ',
                       'at the foot of a hill',
                       'sin',
                       'odor',
                       'scar',
                       'shattered',
                       'run',
                       'florescent',
                       'playground',
                       'halloween']
        if prompt == None:
            embed = Embed(
                description=f":x: {ctx.author.mention} Please provide a prompt you're submitting for",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return

        elif prompt.lower() not in prompt_list:
            embed = Embed(
                description=f":x: {ctx.author.mention} Please provide a correct prompt from our prompt list",
                color=0xDD2222)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return

        elif prompt != None:
            regx = re.compile(f"^{prompt}$", re.IGNORECASE)
            check = table.find_one({"authorid":ctx.author.id, "prompts":regx, "guildid":ctx.guild.id})
            if check==None:
                await ctx.send(f"{ctx.author.mention} You haven't submitted for {prompt} yet.")
                return

            elif check['resubmitted'] == True:
                await ctx.send(f"{ctx.author.mention} You've already resubmitted for {prompt} once already, you can resubmit only once")
                return

            elif check['prompts'].lower() == prompt.lower():
                if ctx.message.attachments:
                    for url in ctx.message.attachments:
                        table.update_one({"guildid":ctx.guild.id, "authorid":ctx.message.author.id, "prompts":prompt, 'resubmitted':False}, {"$set":{"content":url.url, "resubmitted":True}})
                        embed = Embed(description=f"{ctx.author.mention} __**Submitted!**__ \n**Prompt:** {prompt} \n**Tag's content: {url.url}**",
                                      colour=0xF893B2)
                        await ctx.send(embed=embed)
                        return
                else:
                    embed = Embed(
                        description=f":x: {ctx.author.mention} Please upload a drawing you're submitting for together with the command like this:",
                        color=0xDD2222)
                    embed.set_image(url='https://i.imgur.com/tqW93GO.png')
                    await ctx.send(embed=embed)
                    await ctx.message.delete()
                    return

    @commands.command()
    @commands.has_any_role('Mods')
    async def submissions(self, ctx):
        def chunks(l, n):
            n = max(1, n)
            return (l[i:i+n] for i in range(0, len(l), n))

        def create_list(lst, n, s, e):
            lst = list(chunks(lst, n))
            for i in lst[s:e]:
                lst = i
            fl = ''
            for n in lst:
                fl = fl + n
            return fl

        cluster = Mongo.connect()
        db = cluster["giffany"]
        table = db['dat']
        names = table.find({"guildid":ctx.guild.id})
        for n in names:
            prompts = table.find({"guildid":ctx.guild.id, "authorid":n["authorid"]})
            for p in prompts:
                counter = table.count_documents({"guildid":ctx.guild.id, "authorid":n["authorid"]})
                author = ctx.guild.get_member(p["authorid"])

                names = [f"{author}|{author.id}: {counter}\n"]
                test = create_list(names, 100, 0, 1)

        await ctx.send(test)


def setup(bot):
    bot.add_cog(dat(bot))
    print('dat module loaded')
