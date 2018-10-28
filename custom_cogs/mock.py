import discord
import random
from discord.ext import commands
from cogs.utils.checks import *

class mock:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def mock(self, ctx, *, msg=""):

		"""
		Use [p]mock to randomized capitalization on a message or string.
		Better random comming soon™

		Usage:

		[p]mock a string
			A sTRiNg

		[p]mock
			laSt SeNT MeSsaGE

		[p]mock <message id>
			THaT mEsSAgE
		"""

			#check for string or message id
		if msg.isdigit():
			async for message in ctx.channel.history(limit=100):
				if msg == str(message.id):
					msg = message.content
		elif msg == "":
			async for message in ctx.channel.history(limit=2):
				msg = message.content

			#randomize
		fakeresult = ""
		for char in msg:
			value = random.choice([True, False])
			if value == True:
				fakeresult += char.upper()
			if value == False:
				fakeresult += char.lower()

			#ensure random isn't too random™
		caps = ""
		for char in fakeresult:
			if char.isupper():
				caps += "1"
			else:
				caps += "0"
		while "000" in caps or "111" in caps:
			caps = caps.replace("111", "101").replace("000", "010")
		result = ""
		for idx, char in enumerate(fakeresult):
			if caps[idx] == "0":
				result += char.lower()
			else:
				result += char.upper()

		await ctx.message.delete()

		if result == "":
			await ctx.send(self.bot.bot_prefix + "It appears as if you have attempted to dispatch a blank message. This is invalid. It is possible you have proposed a mock of an embeded message.")
		else:
			await ctx.send(result)

def setup(bot):
	bot.add_cog(mock(bot))

# Thanks for the help Lyric.
