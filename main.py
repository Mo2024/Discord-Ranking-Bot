import os
import discord
from discord.ext import commands 
import sqlite3
from sqlite3 import connect


intents = discord.Intents.default() 
intents.members = True
client = commands.Bot(command_prefix = '?',intents=intents) #sets prefix 
client.remove_command('help')

f = 19
m = 0 
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity= discord.Activity(name="Around ;) | ?help", type=discord.ActivityType.watching))
    print('ready')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
@commands.has_role('hehe')
@client.command()
async def clear(ctx, amount=5):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount) 
    await ctx.send( str(amount) + ' messages has been cleared')

@client.command()
async def ping(ctx):
    await ctx.send('Latency is {0}.'.format(round(client.latency, 1)))

@commands.has_role('moh')
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command(aliases=['h'])
async def help(ctx):
    embed = discord.Embed(description = f"**How it works?** \n Use the prefix `?` and next to it one of the commands listed below \n \n **Commands** \n`help` or `h`\n`leaderboard` or `l`\n`add`\n`userinfo`or`ui`\n`top number`\n`remove` or `r` \n \n **Events** \n `@user beat @user` ", color=0xfaa31e)
    await ctx.channel.send(embed=embed)

@commands.has_role('moh')
@client.command()
async def unload (ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')





client.run('ODA2Nzk3NzMxMjA0Njk0MDE2.YBuq8A.V78ZqJBV6fPQKcSd-I6wpImGtZ0') #You know what this is fuck off

