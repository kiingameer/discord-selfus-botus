from discord.ext import commands
from lxml import etree
from random import randint
import discord
import requests

'''Booru cog'''


class Booru:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def danbooru(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from danbooru

        Usage: [p]danbooru <tags>
        If used in a non-NSFW channel, forces `rating:safe`. In NSFW channels, all (dan)booru rating tags work.'''

        temp = taglist_sanitise(ctx, tagstring, filter=False)  # Solves tag limit problem by removing the filter
        tags, rating = temp

        # Only danbooru has a stupid 2 tag limit hence why this tidbit isnt part of the sanitization function,
        # other boorus don't have it, but somehow danbooru does. TODO: auth
        max_tags, plural = (1, '') if rating else (2, 's')
        if len(tags) > max_tags:
            await ctx.send(self.bot.bot_prefix + 'Unauthorised for more than {0} tag{1} - matching based on cap of {0}'
                           .format(max_tags, plural))
            tags = set(list(tags)[:max_tags])  # Sets don't support indexing directly

        # Adds the rating tags on at the end, after truncation
        tags.update(rating)

        # Danbooru requires no prefix
        embed = generic_booru(ctx, 'https://danbooru.donmai.us/posts.json?tags=',
                              tags, 'http://danbooru.donmai.us/posts/', 'Danbooru')

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(aliases=['e926'])
    async def e621(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from e621

        Usage: [p]e621 <tags>
        If used in a non-NSFW channel, forces `rating:safe`. In NSFW channels, all (dan)booru rating tags work.

        Invoke with [p]e926 to only return safe results.'''

        temp = taglist_sanitise(ctx, tagstring)
        # Calling with e926? Doesn't matter, rating is always safe. No exceptions.
        tags, rating = temp[0], ['rating:safe'] if ctx.invoked_with == 'e926' else temp[1]

        # Adds the rating tags on at the end, after truncation
        tags.update(rating)

        # e621 and e926 require no url prefix
        embed = generic_booru(ctx, 'https://{0}.net/post/index.json?tags='.format(ctx.invoked_with),
                              tags, 'http://{0}.net/post/show/'.format(ctx.invoked_with), ctx.invoked_with)

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def hypnohub(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from hypnohub

        Usage: [p]hypnohub <tags>
        If used in a non-NSFW channel, forces `rating:safe`. In NSFW channels, all (dan)booru rating tags work.'''

        temp = taglist_sanitise(ctx, tagstring)
        tags, rating = temp

        # Adds the rating on at the end, after truncation
        tags.update(rating)

        # hypnohub requires only https:
        embed = generic_booru(ctx, 'https://hypnohub.net/post.json?tags=', tags,
                              'http://hypnohub.net/post/show/', 'hypnohub', 'https:')

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            # Special handling due to really silly hypnohub admins
            embed.set_image(url=embed.image.url.replace('.net//', '.net/'))
            await ctx.send(embed=embed)

#    @commands.command()
    async def lolibooru(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from Lolibooru

        Usage: [p]lolibooru <tags>
        If used in a non-NSFW channel, forces `rating:safe`. In NSFW channels, all (dan)booru rating tags work.'''

        #  Note: this command is disabled by default - to enable, remove the # 7 lines up
        temp = list(set(tagstring.split()) & {'loli', 'shota', 'toddlercon'})
        tags, rating = taglist_sanitise(ctx, tagstring, filter=False)

        tags.update(rating)
        tags.update(temp)

        embed = generic_booru(ctx, 'https://lolibooru.moe/post/index.json?tags=', tags,
                              'https://lolibooru.moe/post/show/', 'Lolibooru')

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def paheal(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from paheal

        Usage: [p]paheal <tags>
        This can only be used in NSFW channels due to the nature of paheal.'''
        if type(ctx.channel) is discord.DMChannel or type(ctx.channel) is discord.GroupChannel or not ctx.channel.is_nsfw():
            await ctx.message.delete()
            await ctx.send(self.bot.bot_prefix + 'Not in a NSFW channel', delete_after=3.0)
            print('DEBUG: This command cannot be used in SFW channels')
            return

        temp = taglist_sanitise(ctx, tagstring)
        tags = temp[0]  # We don't care about rating

        # paheal has no prefix
        embed = generic_booru(ctx, 'http://rule34.paheal.net/api/danbooru/find_posts?tags=',
                              tags, 'http://rule34.paheal.net/post/view/', 'Paheal')

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(aliases=['r34'])
    async def rule34(self, ctx, *, tagstring: str):
        '''Gets the first image matching `tagstring` from rule34

        Usage: [p]rule34|r34 <tags>
        This can only be used in NSFW channels due to the nature of rule34.'''

        if not ctx.channel.is_nsfw():
            await ctx.message.delete()
            await ctx.send(self.bot.bot_prefix + 'Not in a NSFW channel', delete_after=3.0)
            print('DEBUG: This command cannot be used in SFW channels')
            return

        temp = taglist_sanitise(ctx, tagstring)
        tags = temp[0]  # We don't care about rating

        # rule34 has https:
        embed = generic_booru(ctx, 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags=',
                              tags, 'http://rule34.xxx/index.php?page=post&s=view&id=', 'rule34',
                              'https:')

        if type(embed) is str:
            await ctx.send(self.bot.bot_prefix + embed)
        else:
            await ctx.send(embed=embed)


def generic_booru(ctx, api_url, taglist, post_url, name, prefix=''):
    '''Return an embed using generic parameters'''
    tags = '+'.join(taglist)

    req = request(api_url, tags, prefix)
    embed, image_id = req

    if embed == 'no_img':
        return 'No images match that search'
    elif image_id is None:
        print(embed)
        return 'Something broke: consult console for details'

    create_embed_title(post_url, image_id, '', name, embed)

    return embed


def request(api_url, tag_string, url_prefix=''):
    '''Return a tuple with an embed containing the file URL from the requested server and the id of the post'''
    # Query api_url
    is_down = ' - is this booru down for you, or blocked?'
    try:
        api_request = requests.get(api_url + tag_string, headers={"user-agent": "ev1l0rd/Booru"}, timeout=10)
    except requests.exceptions.ConnectionError:
        return ('DEBUG: Connection error' + is_down, None)
    except requests.exceptions.Timeout:
        return ('DEBUG: Connection timed out' + is_down, None)

    if api_request.status_code != 200:
        return ('DEBUG (send to HM892#8264): HTTP error {0} URL: {1}'.format(api_request.status_code, api_url + tag_string), None)

    try:
        req = api_request.json()
    except ValueError:
        req = etree.fromstring(api_request.content)

    temp_len = len(req)
    try:
        temp = req[randint(0, 9 if temp_len > 10 else temp_len - 1)]
    except ValueError:
        return ('no_img', None)  # This happens if, say, an id:int tag doesn't exist

    try:
        base_url = temp.get('file_url')
        image_id = temp.get('id')
    except (KeyError, IndexError) as e:
        for post in req:
            try:
                base_url = post.get('file_url')
                image_id = post.get('id')
                break
            except (KeyError, IndexError) as e:
                continue
        else:
            return ('no_img', None)

    ret_val = discord.Embed(type='rich')
    ret_val.set_image(url=url_prefix + base_url)  # Ensures URL is correct

    return (ret_val, image_id)


def taglist_sanitise(ctx, tagstring, filter=True):
    '''Sanitize the taglist input of disallowed tags, and corrects ratings.'''

    # list() of items to sanitise
    sanitise_list = ['safe', 'rating:safe', 'rating:s', 'questionable', 'rating:questionable',
                     'rating:q', 'explicit', 'rating:explicit', 'rating:e', 'loli', 'shota', 'toddlercon']

    # Input arg `tagstring` -> set() - this disallows duplicates (and therefore lets sanitise() work)
    tags = set(tagstring.split())

    # Ratings list to be appended - this is separate to prevent meta tags being counted or affected by local code
    rating = []

    safe = ['safe', 'rating:safe', 'rating:s']
    questionable = ['questionable', 'rating:questionable', 'rating:q']
    explicit = ['explicit', 'rating:explicit', 'rating:e']

    if type(ctx.channel) is discord.DMChannel or type(ctx.channel) is discord.GroupChannel or not ctx.channel.is_nsfw():
        rating.append('rating:safe')
    else:
        # This block ensures that a) the correct rating is set, based on rating metatags,
        # and b) that there is only one rating tag
        for tag in tags:
            if tag in safe:
                rating.append('rating:safe')
                break
            elif tag in questionable:
                rating.append('rating:questionable')
                break
            elif tag in explicit:
                rating.append('rating:explicit')
                break

    # Lolicon, shotacon and toddlercon are explicitly disallowed by the ToS
    if filter:
        rating += ['-loli', '-shota', '-toddlercon']

    # Returns a set of all tags that aren't ratings and the rating list itself
    return (tags.difference(sanitise_list), rating)


def create_embed_title(base, post_id, suffix, titletext, embed):
    '''Constructs the post url and sets it to the embed title'''
    embed.url = base + str(post_id) + suffix
    embed.title = '{0} - Post {1}'.format(titletext, post_id)


def setup(bot):
    bot.add_cog(Booru(bot))
