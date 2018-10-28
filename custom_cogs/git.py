import discord
import subprocess
import os
import git
from discord.ext import commands
import asyncio

'''Code to switch between branches'''

class Git:
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(pass_context=True, invoke_without_command=True)
    async def git(self, ctx, *, branch):
        """Switch between branches"""
        if ctx.invoked_subcommand is None:
            g = git.cmd.Git(working_dir=os.getcwd())
            branchversion = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            if branch != branchversion:
                exit_code = g.execute(['git', 'stash'])
                if exit_code != "No local changes to save":
                    await ctx.send(self.bot.bot_prefix + "Stashed changes to " + branchversion + ".")
                exit_code = g.execute(['git', 'checkout', branch])
                exit_code = g.execute(['git', 'pull', 'origin', branch])
                if exit_code != "Already up-to-date.":
                    await ctx.send(self.bot.bot_prefix + "Pulled latest changes to " + branch + ".")
                stash = g.execute(['git', 'stash', 'list'])
                if stash != "\n":
                    try:
                        exit_code = g.execute(['git', 'stash', 'apply'])
                        if exit_code:
                            await ctx.send(self.bot.bot_prefix + "Applied stashed changes")
                    except:
                        pass
                await ctx.send(self.bot.bot_prefix + "Successfully checked out branch {}!".format(branch))
                if os.name == 'nt':
                    os.system('cls')
                else:
                    try:
                        os.system('clear')
                    except:
                        pass
                print('Logged in as')
                try:
                    print(self.bot.user.name)
                except:
                    pass
                print('User id:' + str(self.bot.user.id))
                print('Current branch is: ' + branch)
                print('------')
                print(stash)
            else:
                await ctx.send(self.bot.bot_prefix + "You're already on that branch!")
            
    @git.command()
    async def pull(self, ctx):
        """Pull changes for the current branch"""
        await ctx.message.delete()
        g = git.cmd.Git(working_dir=os.getcwd())
        branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        try:
            exit_code = g.execute(['git', 'pull', 'origin', branch])
        except:
            return await ctx.send(self.bot.bot_prefix + "Couldn't pull changes, most likely due to files requiring stashing. Please run `git stash` then try again.")
        if exit_code != "Already up-to-date.":
            await ctx.send(self.bot.bot_prefix + "Pulling latest changes to " + branch + "...")
            await ctx.send(self.bot.bot_prefix + "Successfully pulled {}!".format(branch))
            print('Restarting...')
            with open('restart.txt', 'w', encoding="utf8") as re:
                re.write(str(ctx.message.channel.id))
            await ctx.send(self.bot.bot_prefix + "Restarting to apply changes...")
            if self.bot.subpro:
                self.bot.subpro.kill()
            os._exit(0)
        else:
            await ctx.send(self.bot.bot_prefix + "There were no changes to pull.", delete_after=10)
        
    @git.command()
    async def branch(self, ctx):
        """Check current branch"""
        await ctx.message.delete()
        g = git.cmd.Git(working_dir=os.getcwd())
        branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        await ctx.send(self.bot.bot_prefix + "Current branch is: " + branch, delete_after=20)
        
        
    @git.group(invoke_without_command=True)
    async def stash(self, ctx):
        """Stash changes"""
        g = git.cmd.Git(working_dir=os.getcwd())
        branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        exit_code = g.execute(['git', 'stash'])
        if exit_code != "No local changes to save":
            await ctx.send(self.bot.bot_prefix + "Stashed changes to " + branch + ".")
        else:
            await ctx.send(self.bot.bot_prefix + "There was nothing to stash!")
        
        
    @stash.command()
    async def clear(self, ctx):
        """Clear all stashed files"""
        def check(msg):
            if msg:
                return (msg.content.lower().strip() == 'yes' or msg.content.lower().strip() == 'no') and msg.author == self.bot.user
            else:
                return False
        g = git.cmd.Git(working_dir=os.getcwd())
        await ctx.send(self.bot.bot_prefix + "Are you sure you want to clear stashed files? `yes` or `no`.")
        reply = await self.bot.wait_for("message", check=check)
        if reply.content.lower() == "yes":
            clear = g.execute(["git", "stash", "clear"])
            await ctx.send(self.bot.bot_prefix + "Cleared stashed files.")
        if reply.content.lower() == "no":
            await ctx.send(self.bot.bot_prefix + "Canceled stash clearing.")
            return
        
    @stash.command()
    async def apply(self, ctx):
        """Apply stashed files"""
        g = git.cmd.Git(working_dir=os.getcwd())
        exit_code = g.execute(['git', 'stash', 'apply'])
        if exit_code:
            await ctx.send(self.bot.bot_prefix + "Applied stashed changes")
        else:
            await ctx.send(self.bot.bot_prefix + "There were no stashed changes to apply")
    
def setup(bot):
    bot.add_cog(Git(bot))
