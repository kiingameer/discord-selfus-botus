from discord.ext import commands
import re


'''Linksplit cog'''


class Linksplit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def linksplit(self, ctx, *msg):
        '''Splits provided links into chunks of 5, so that they can all embed at once.

        Usage: [p]linksplit <links>
        Note that this splits on *all* links, regardless of embeddability.
        '''
        await ctx.message.delete()
        # This regex needs to never exist again.
        r = re.compile(r"https?://(([\w{0}])+\.)+([/{0}])*\.?\w*((#|\?)([\w{0}=])+)?(&[\w{0}=]+)*".format("$\-+!*'(),"))
        temp = [link for link in msg if r.match(link)]
        for msg in [temp[i:i + 5] for i in range(0, len(temp), 5)]:
            await ctx.send('\n'.join(msg))


def setup(bot):
    bot.add_cog(Linksplit(bot))
