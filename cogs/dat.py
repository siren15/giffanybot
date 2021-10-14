import discord
from discord import Embed
from discord.ext import commands

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
        prompt_list = ['01. wandering',
                       '02. trail',
                       '03. fall',
                       '04. deep',
                       '05. crooked',
                       '06. screech',
                       '07. a closet ',
                       '08. "at the foot of a hill"',
                       '08. at the foot of a hill',
                       '09. sin',
                       '10. odor',
                       '11. scar',
                       '12. shattered',
                       '13. run',
                       '14. florescent',
                       '15. playground',
                       'Bonus: halloween',
                       'wandering',
                       'trail',
                       'fall',
                       'deep',
                       'crooked',
                       'screech',
                       'a closet ',
                       '"at the foot of a hill"',
                       'at the foot of a hill',
                       'sin',
                       'odor',
                       'scar',
                       'shattered',
                       'run',
                       'florescent',
                       'playground',
                       'halloween',
                       '01 wandering',
                       '02 trail',
                       '03 fall',
                       '04 deep',
                       '05 crooked',
                       '06 screech',
                       '07 a closet ',
                       '08 "at the foot of a hill"',
                       '08 at the foot of a hill',
                       '09 sin',
                       '10 odor',
                       '11 scar',
                       '12 shattered',
                       '13 run',
                       '14 florescent',
                       '15 playground',
                       'Bonus halloween',
                       '1 wandering',
                       '2 trail',
                       '3 fall',
                       '4 deep',
                       '5 crooked',
                       '6 screech',
                       '7 a closet ',
                       '8 "at the foot of a hill"',
                       '8 at the foot of a hill',
                       '9 sin',
                       '10 odor',
                       '11 scar',
                       '12 shattered',
                       '13 run',
                       '14 florescent',
                       '15 playground',
                        '1. wandering',
                        '2. trail',
                        '3. fall',
                        '4. deep',
                        '5. crooked',
                        '6. screech',
                        '7. a closet ',
                        '8. "at the foot of a hill"',
                        '8. at the foot of a hill']
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

        elif prompt.lower() != None:
            regx = re.compile(f"^{prompt}$", re.IGNORECASE)
            check = table.find({"authorid":ctx.author.id, "prompts":regx, "guildid":ctx.guild.id})
            ch = [n['prompt'] for n in check]
            if ch != []:
                embed = Embed(
                    description=f":x: {ctx.author.mention} You already submitted for this prompt already, if you want to resubmit you can one time for each prompt using .resubmit 'prompt name' with uploading the correct drawing in one message",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                await ctx.message.delete()
                return

        if ctx.message.attachments==True:
            for url in ctx.message.attachments:
                table.insert_one({"guildid":ctx.guild.id, "authorid":ctx.message.author.id, "prompts":prompt, "content":url.url})
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

        def newpage(names, counter, pages):
            embed = Embed(description=f"__**Listing info about submissions for draw-a-thon 2021**__",
            colour=0xF893B2)
            embed.add_field(name="User names:", value=f"{names}")
            embed.add_field(name="Submission counter:", value=f"{counter}")
            embed.set_footer(text=pages)
            return embed

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']


        cluster = Mongo.connect()
        db = cluster["giffany"]
        tag_names = db['dat'].find({"guildid":ctx.guild.id})
        names = [str(name['authorid'])+"\n" for name in tag_names]

        counter = db['dat'].find({"guildid":ctx.guild.id})
        counter =  [str(c['authorid'])+"\n" for c in counter]

        if names == []:
            embed = Embed(description=f"There are no submissions yet.",
                          colour=0xF893B2)
            await ctx.send(embed=embed)
            return

        s = 0
        e = 1
        counter = 1

        nc = list(chunks(names, 20))

        footer = f"Page:{counter}|{len(nc)}"
        embedl = await ctx.send(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
        await embedl.add_reaction('⬅️')
        await embedl.add_reaction('➡️')

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            except asyncio.TimeoutError:
                await embedl.clear_reactions()
                break

            if (reaction.emoji == '➡️') and (counter < len(nc)):
                counter = counter + 1
                s = s + 1
                e = e + 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
                await embedl.remove_reaction('➡️', ctx.author)
            else:
                await embedl.remove_reaction('➡️', ctx.author)

            if (reaction.emoji == '⬅️') and (counter > 1):
                counter = counter - 1
                s = s - 1
                e = e - 1
                footer = f"Page:{counter}|{len(nc)}"
                await embedl.edit(embed=newpage(create_list(names, 20, s, e), ctx.guild, footer))
                await embedl.remove_reaction('⬅️', ctx.author)
            else:
                await embedl.remove_reaction('⬅️', ctx.author)










def setup(bot):
    bot.add_cog(dat(bot))
    print('dat module loaded')
