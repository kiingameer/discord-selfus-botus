#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-

# This cog by HarJIT may be used, etc in its entirety under the same terms as Appu's selfbot itself (GPLv3).

# This cog may alternatively be used, etc as outlined in the Mozilla Public License (any version).  To be clear, 
# these alternative terms apply to this file alone and not to any other selfbot component or dependency.

# HarJIT supplies this free of charge with no guarantee of safety, fitness, accuracy or anything else.

import discord, cogs.utils.checks, discord.ext.commands

import getopt, io

def describe(i, showlevel):
    r = ""
    if i.mentionable:
        r += ", mentionable"
    if i.hoist:
        r += ", hoisted"
    if i.color.value:
        r += ", #%06x" % i.color.value
    else:
        r += ", colourless"
    if i.managed:
        r += ", managed"
    if showlevel:
        r += ", role level %d" % i.position
    return r.lstrip(" ,")

def pad(s):
    if len(s) < 20:
        s += "\x20" * (20 - len(s))
    return s

async def softsend(mybot, ctx, f, prefix="", suffix=""):
    if hasattr(mybot, "send_message"):
        send_message = mybot.send_message
    else:
        send_message = (lambda ctx, m: ctx.send(m))
    r = ""
    f.seek(0)
    lines = f.readlines()
    limit = 2000 - len(suffix)
    while lines:
        #print(lines)
        cut = limit - len(r)
        line = lines.pop(0)
        if (len(line) > limit) and (cut > 0):
            # Because pushing on front, have to push in reverse order.
            lines.insert(0, line[cut:])
            lines.insert(0, line[:cut])
        elif len(r + line) > limit:
            lines.insert(0, prefix + line)
            await send_message(ctx.message.channel, r + suffix)
            r = ""
        else:
            r += line
    if r:
        await send_message(ctx.message.channel, r)

async def notification(mybot, ctx, message):
    print("NOTIFY:", message)
    await softsend(mybot, ctx, io.StringIO(mybot.bot_prefix + message))

class Listroles(object):
    def __init__(self, mybot):
        self.mybot = mybot
    @discord.ext.commands.group(pass_context = True)
    async def listroles(self, ctx):
        """List roles on a server by number of members.  Accepts --all, --color, --min=(number), --level.
        
        --all: List all roles.  This overrides --min and --color.
        
        --color: List only roles with a colour.
        
        --level: Show the roles' positions in the configured order (does not affect sorting).
        
        --min=(number): Minimum number of members for a role to be displayed.  Default 2.
        """
        server = ctx.message.server if hasattr(ctx.message, "server") else ctx.message.guild
        argv = ctx.message.content[cogs.utils.checks.cmd_prefix_len():]
        argv = argv.strip().split()
        option_names = ["colour", "color", "all", "min=", "level"]
        option_string = ""
        option_expand = {}
        for i in option_names:
            if i[0] not in option_string:
                colon = ":" if (i[-1] == "=") else ""
                option_string += i[0] + colon
                option_expand["-" + i[0]] = "--" + i.rstrip("=")
        try:
            optsv, args = getopt.gnu_getopt(argv[1:], option_string, option_names)
        except Exception as e:
            await notification(self.mybot, ctx, str(e))
            return
        opts = {}
        for k, v in optsv:
            if k in option_expand:
                k = option_expand[k]
            opts[k] = v
        try:
            minimum = int(opts["--min"]) if "--min" in opts else 2
        except ValueError as e:
            await notification(self.mybot, ctx, str(e))
            return
        showlevel = "--level" in opts
        #
        counts = {}
        roles = list(server.roles)[:]
        for i in roles:
            counts[i.id] = 0
        for i in server.members:
            for j in i.roles:
                counts[j.id] += 1
        roles.sort(key = lambda i: -counts[i.id])
        #
        out = io.StringIO()
        out.write(self.mybot.bot_prefix+"```\n")
        for i in roles:
            if "--all" not in opts:
                if ("--color" in opts or "--colour" in opts) and not i.color.value:
                    continue
                elif counts[i.id] < minimum:
                    continue
            print(pad("%s: %d" % (i.name, counts[i.id])) + "(" + describe(i, showlevel) + ")", file=out)
        out.write("\n```")
        await softsend(self.mybot, ctx, out, "```\n", "\n```")

def setup(mybot):
    mybot.add_cog(Listroles(mybot))
