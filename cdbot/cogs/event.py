from cdbot.constants import QUESTION_CHANNEL_ID
from discord.ext.commands import Bot, Cog, Context, command
from discord import Embed


class Event(Cog):
    """
    Event functionality
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_message")
    async def register_question(self, message):
        if message.channel.id == QUESTION_CHANNEL_ID:
            # Firstly, sanitise the message.
            # Questions should not have attachments.
            if len(message.attachments) > 0:
                return
            # Posted in the question channel, add the upvote reaction, ready for the other functionality.
            await message.add_reaction("👍")

    @command()
    async def fetchQuestions(self, ctx, count=1):
        # We want to iterate through every message in the question channel.
        targetChannel = self.bot.get_channel(QUESTION_CHANNEL_ID)
        questions = []
        async for message in targetChannel.history():
            thumbCount = None
            alreadyUsed = False
            # Questions will be sorted by the number of votes they have, and then which one is older.
            for reaction in message.reactions:
                if str(reaction.emoji) == "👍":
                    thumbCount = reaction.count - 1 # The bot's reaction doesn't count.
                if str(reaction.emoji) == "✅":
                    # Question already answered, we don't add it to the list.
                    alreadyUsed = True
            if thumbCount != None and not alreadyUsed: # After all iteration is done...
                questions.append((message,thumbCount,message.created_at)) # Add the tuple to our list.
        # Now we have all the questions in a list, we need to sort them.
        questions.sort(key=lambda a: (-a[1],a[2]))
        # Now, only use the top X questions.
        if len(questions) == 0:
            await ctx.send("We're out of questions!")
        for question in questions[:count]:
            embed = Embed()
            embed.set_author(name=str(question[0].author),icon_url=question[0].author.avatar_url)
            embed.colour = question[0].author.top_role.colour
            embed.description = question[0].content
            embed.timestamp = question[0].created_at
            await question[0].add_reaction("✅")
            await ctx.send(embed=embed)

    @command()
    async def purgeQuestions(self, ctx):
        targetChannel = self.bot.get_channel(QUESTION_CHANNEL_ID)
        await targetChannel.purge()

def setup(bot):
    """
    Required boilerplate for adding functionality of cog to bot.
    """
    bot.add_cog(Event(bot))