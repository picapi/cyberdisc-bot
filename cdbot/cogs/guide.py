from discord.ext import commands
from discord.ext.commands import command, Context
from discord.ext.commands import Bot, Cog
from discord import Embed, ChannelType
from json import load
from re import match

class Guide(Cog):
    """
    A system which allows a navigatable guide in Discord DMs.
    """
    with open("cdbot/data/guide/guide.json","r", encoding="UTF-8") as f:
        guideInfo = load(f)
    pages = {}
    for p in guideInfo["pages"]:
        if not p.get("content", None):
            if p.get("contentFile"):
                with open("cdbot/data/guide/pages/{}".format(p.get("contentFile")),"r",encoding="UTF-8") as c:
                    content = c.read()
                    p["content"] = content
            else:
                print("No content found!")
        pages[p.get("tag")] = p

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.dm_only()
    @command()
    async def guide(self, ctx, pageid : str="Tutorial Introduction"):
        '''
        Returns the guide page provided, or the default if none are provided.
        '''
        return await self.sendGuide(ctx.message.author,pageid)

    @command()
    async def tutorial(self, ctx):
        '''
        Stars a Tutorial
        '''
        return await self.sendGuide(ctx.message.author, "Tutorial Introduction")

    async def sendGuide(self,user,pageid):
        pageToShow = self.pages.get(pageid)
        if pageToShow:
            embed = self.getEmbedForPage(pageToShow)
            m = await user.send(embed=embed)
            for r in pageToShow.get("options", {}).keys():
                print(r)
                await m.add_reaction(r)
        return True


    def getEmbedForPage(self, pageToShow):
        print(pageToShow)
        e = Embed()
        e.title = pageToShow["title"]
        e.description = pageToShow["content"]
        for k,v in pageToShow.get("fields",{}).items():
            e.add_field(name=k,value=v)
        e.set_footer(text="📚 Guide System | Tag: {}".format(pageToShow['tag']))
        print(e)
        return e

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Need to perform some checks.
        user = await self.bot.fetch_user(payload.user_id)
        if user == self.bot.user:
            return
        channel = await self.bot.fetch_channel(payload.channel_id)
        if channel.type != ChannelType.private:
            return
        message = await channel.fetch_message(payload.message_id)
        if not len(message.embeds) > 0:
            return
        m = match("📚 Guide System \| Tag: (.*)",message.embeds[0].footer.text)
        print(m)
        targetPage = m.group(1)
        if targetPage:
            # We have a guide page, now see if a trigger should happen.
            # Get the relevant page from memory.
            page = self.pages.get(targetPage)
            if page:
                nextPage = page['options'].get(str(payload.emoji))
                if nextPage:
                    await self.sendGuide(user,nextPage)

def setup(bot):
    bot.add_cog(Guide(bot))