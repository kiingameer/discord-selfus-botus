from discord.ext import commands

class Wide:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def wide(self, ctx, *, msg=""):
		"""
		I don't know... It makes the text wide or fullwidth or something like that.
		Usage:

		[p]wide <a string that you wish to be wide>
			ＮＯＷ　ＹＯＵＲ　ＳＴＲＩＮＧ　ＩＳ　ＷＩＤＥ

		[p]wide
			ＬＡＳＴ ＭＥＳＳＡＧＥ: ＷＩＤＥ ＥＤＩＴＩＯＮ

		[p]wide <message id of message that you wish to be wide>
			ＭＥＳＳＡＧＥ　ＣＯＮＴＥＮＴＳ　ＯＮＬＹ　ＷＩＤＥ
		"""

			#check for string or message id
		if msg.isdigit():
			async for message in ctx.channel.history(limit=100):
				if msg == str(message.id):
					msg = message.content
		elif msg == "":
			async for message in ctx.channel.history(limit=2):
				msg = message.content

		widedict= {
		"A": "Ａ",
		"B": "Ｂ",
		"C": "Ｃ",
		"D": "Ｄ",
		"E": "Ｅ",
		"F": "Ｆ",
		"G": "Ｇ",
		"H": "Ｈ",
		"I": "Ｉ",
		"J": "Ｊ",
		"K": "Ｋ",
		"L": "Ｌ",
		"M": "Ｍ",
		"N": "Ｎ",
		"O": "Ｏ",
		"P": "Ｐ",
		"Q": "Ｑ",
		"R": "Ｒ",
		"S": "Ｓ",
		"T": "Ｔ",
		"U": "Ｕ",
		"V": "Ｖ",
		"W": "Ｗ",
		"X": "Ｘ",
		"Y": "Ｙ",
		"Z": "Ｚ",
		"a": "ａ",
		"b": "ｂ",
		"c": "ｃ",
		"d": "ｄ",
		"e": "ｅ",
		"f": "ｆ",
		"g": "ｇ",
		"h": "ｈ",
		"i": "ｉ",
		"j": "ｊ",
		"k": "ｋ",
		"l": "ｌ",
		"m": "ｍ",
		"n": "ｎ",
		"o": "ｏ",
		"p": "ｐ",
		"q": "ｑ",
		"r": "ｒ",
		"s": "ｓ",
		"t": "ｔ",
		"u": "ｕ",
		"v": "ｖ",
		"w": "ｗ",
		"x": "ｘ",
		"y": "ｙ",
		"z": "ｚ",
		"1": "１",
		"2": "２",
		"3": "３",
		"4": "４",
		"5": "５",
		"6": "６",
		"7": "７",
		"8": "８",
		"9": "９",
		"0": "０",
		"!": "！",
		"?": "？",
		" ": "　"
		}

		result = msg.translate(str.maketrans(widedict))

		await ctx.message.delete()

		if result == "":
			await ctx.send(self.bot.bot_prefix + "Looks like you tried to send an emtpy message! This is usually caused by trying to wideify an embeded message.")
		else:
			await ctx.send(result)

def setup(bot):
	bot.add_cog(Wide(bot))

#Lyric you halp me so much
