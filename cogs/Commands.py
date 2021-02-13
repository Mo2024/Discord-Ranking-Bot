import discord
from discord.ext import commands 
import random
from discord import Color
import string 
import sqlite3
from sqlite3 import connect
import functools
from prettytable import PrettyTable 
import itertools
from PIL import Image, ImageDraw
import io

first = None
second = None
third = None

def ranking_function():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT Points, Wins, Loss, Win_Loss_Ratio, row_rank FROM main ORDER BY Points DESC;")
    test = cursor.fetchall()
    largest = 9999999999999999999999999999
    rank = 0
    for table in test:
        if table[0] < largest:
            print(table[0])
            largest = table[0]
            print(largest)
            rank = rank + 1
            cursor.execute(f"UPDATE main SET row_rank = {rank} WHERE Points = {table[0]}")
            db.commit()
        elif table[0] == largest:
            cursor.execute(f"UPDATE main SET row_rank = {rank} WHERE Points = {table[0]}")
            db.commit()
            
class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        print('Commands shii are working')

    @commands.Cog.listener()
    async def on_message(self, message):
        global first
        global second
        global third
    

        if "beat" in message.content.lower() and "@" in message.content.lower():
            try:
                db = sqlite3.connect('main.sqlite')
                cursor = db.cursor()
                first, second, third = message.content.split()
                print(first,second)
                if "<@!" in first and "<@!" in third:
                    winner_id = first.replace('<@!','')
                    winner_id = winner_id.replace('>','')
                    loser_id = third.replace('<@!','')
                    loser_id = loser_id.replace('>','')
                    winner_id = winner_id.replace('!','')
                    loser_id = loser_id.replace('!','')

                elif "<@" in first and "<@" in third:
                    winner_id = first.replace('<@','')
                    winner_id = winner_id.replace('>','')
                    loser_id = third.replace('<@','')
                    loser_id = loser_id.replace('>','')
                    winner_id = winner_id.replace('!','')
                    loser_id = loser_id.replace('!','')


                print(loser_id,winner_id)

                if loser_id == winner_id: 
                    await message.channel.send("You cannot beat yourself, please use the event coorectly")
                else:


                    # selects the players points
                    cursor.execute(f"SELECT Points FROM main WHERE Players = {int(winner_id)} ")
                    old_winner_points = cursor.fetchone()
                    old_winner_points = functools.reduce(lambda sub, ele: sub * 10 + ele, old_winner_points) 
                    cursor.execute(f"SELECT Points FROM main WHERE Players = {int(loser_id)} ")
                    old_loser_points = cursor.fetchone()
                    old_loser_points = functools.reduce(lambda sub, ele: sub * 10 + ele, old_loser_points) 

                    # calculations 
                    EWinner = 1/(1+10**((old_loser_points - old_winner_points)/400))
                    Eloser = 1/(1+10**((old_winner_points - old_loser_points)/400))
                    winner_updated_points= old_winner_points + 16*(1-EWinner)
                    loser_updated_points = old_loser_points + 16*(0-Eloser)

                    if loser_updated_points < 0:
                        loser_updated_points = 0
                    elif winner_updated_points < 0:
                        winner_updated_points = 0 

                    cursor.execute(f"UPDATE main SET Points = {round(winner_updated_points,1)} WHERE Players = {int(winner_id)}")
                    cursor.execute(f"UPDATE main SET Wins = Wins + {1} WHERE Players = {int(winner_id)}")
                    cursor.execute(f"UPDATE main SET Points = {round(loser_updated_points,1)} WHERE Players = {int(loser_id)}")
                    cursor.execute(f"UPDATE main SET Loss = Loss + {1} WHERE Players = {int(loser_id)}")
                    db.commit()

                    cursor.execute(f"SELECT Wins FROM main WHERE Players = {int(winner_id)} ")
                    nowow = cursor.fetchone()
                    nowow = functools.reduce(lambda sub, ele: sub * 10 + ele, nowow) 
                    cursor.execute(f"SELECT Loss FROM main WHERE Players = {int(winner_id)} ")
                    nolow = cursor.fetchone()
                    nolow = functools.reduce(lambda sub, ele: sub * 10 + ele, nolow)
                    if nowow >= 1 and nolow == 0:
                        winnerratio = nowow/1
                    else:
                        winnerratio = nowow/nolow

                    cursor.execute(f"SELECT Wins FROM main WHERE Players = {int(loser_id)} ")
                    nowol = cursor.fetchone()
                    nowol = functools.reduce(lambda sub, ele: sub * 10 + ele, nowol) 
                    cursor.execute(f"SELECT Loss FROM main WHERE Players = {int(loser_id)} ")
                    nolol = cursor.fetchone()
                    nolol = functools.reduce(lambda sub, ele: sub * 10 + ele, nolol)
                    if nowol >= 1 and nolol == 0:
                        loserratio = nowol/1
                    else:
                        loserratio = nowol/nolol

                    cursor.execute(f"UPDATE main SET Win_Loss_Ratio = {round(winnerratio,1)} WHERE Players = {int(winner_id)}")
                    cursor.execute(f"UPDATE main SET Win_Loss_Ratio = {round(loserratio,1)} WHERE Players = {int(loser_id)}")
                    db.commit()
                    ranking_function()
                    cursor.close()
                    db.close
                    await message.channel.send(f"<@!{winner_id}> points = {round(winner_updated_points,1)} and <@!{loser_id}> points = {round(loser_updated_points,1)}")

            except TypeError:
                await message.channel.send("One of the pinged users are not registered in the database. You can add them using `?add @user`")

            except ValueError:
                await message.channel.send("Your format in this event is incorrect. Please make sure its the same as the one shown in `?help`")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        if before.nick != after.nick and after.nick is not None:
            newnick = after.nick
            cursor.execute(f"UPDATE main SET Username_nick = '{newnick}' WHERE Players = {before.id}")
            db.commit()
        elif before.nick != after.nick and after.nick is None:
            cursor.execute(f"UPDATE main SET Username_nick = '{before.name}' WHERE Players = {before.id}")
            db.commit()
        cursor.close()
        db.close



    @commands.command()
    async def top(self, ctx, *, number= None):
        if number is not None:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT row_rank , Username_nick ,Points, Wins, Loss, Win_Loss_Ratio FROM main ORDER BY row_rank ASC")
            result = cursor.fetchmany(int(number))
            x = PrettyTable(["Rank", "Player" ,"Points","Wins","Loss","Ratio"])
            for row in result:
                x.add_row(row)
            height = 80
            for row in x:
                print(row)
                height = height + 13.3333333333333333333333333

    
            img = Image.new('RGB', (410, int(height)), color = (32, 34, 37))
            d = ImageDraw.Draw(img)
            d.text((10,10), f"{x}", fill=(185, 187, 190))
            img.save('pil_text.png')
            file = discord.File("pil_text.png")
            

            embed = discord.Embed(description = f"**TOP {number}**", color=0xfaa31e)
            embed.set_image(url="attachment://pil_text.png")
            await ctx.channel.send(file = file,embed=embed)
        else:
            await ctx.channel.send("Please enter a number like `?top 5`")  


             
    @commands.command(aliases=['r'])
    async def remove(self, ctx, user:discord.User):
        player = user.id
        if ctx.message.author.guild_permissions.administrator:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM main WHERE Players= {int(player)};")
            db.commit()
            ranking_function()
            cursor.close()
            db.close()
            await ctx.channel.send(f"<@!{player}> has been removed")
            

                
    @commands.command()
    async def add(self, ctx, user:discord.Member):
        if user.nick is None:
            nickname = user.display_name
        else:
            nickname = user.nick
        if ctx.message.author.guild_permissions.administrator:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            try:
                cursor.execute(f"INSERT INTO main(Players,Points,Wins,Loss,Win_Loss_Ratio,Username_nick) VALUES(?,?,?,?,?,?)", (user.id,0,0,0,0,nickname))
                db.commit()
                await ctx.send(f"<@!{user.id}> has been added")
                ranking_function()
            except sqlite3.IntegrityError:
                await ctx.send(f"<@{user.id}> is already in teh database")
            cursor.close()
            db.close()

    @commands.command(aliases = ['ui'])
    async def userinfo(self, ctx, member: discord.Member=None):
        if not member:
            member = ctx.message.author    
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT row_rank , Points, Wins, Loss, Win_Loss_Ratio FROM main WHERE Players = {member.id}")
        result = cursor.fetchall()
        x = PrettyTable(["Rank","Points","Wins","Loss","Ratio"])
        for row in result:
            x.add_row(row)

        embed = discord.Embed(description = f"\n \n ```\n{x}```", color=0xfaa31e)
        embed.set_author(name= f"‎{member.name}'s Records", icon_url=member.avatar_url)
        await ctx.channel.send(embed=embed)


    @commands.command(aliases = ['l'])
    async def leaderboard(self, ctx, member: discord.Member=None):
 
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT row_rank , Username_nick ,Points, Wins, Loss, Win_Loss_Ratio FROM main ORDER BY row_rank ASC")
        result = cursor.fetchall()

        x = PrettyTable(["Rank", "Player" ,"Points","Wins","Loss","Ratio"])
        for row in result:
            x.add_row(row)
            
        height = 80
        for row in x:
            print(row)
            height = height + 13.3333333333333333333333333

 
        img = Image.new('RGB', (410, int(height)), color = (32, 34, 37))
        d = ImageDraw.Draw(img)
        d.text((10,10), f"{x}", fill=(185, 187, 190))
        img.save('pil_text.png')
        file = discord.File("pil_text.png")
        

        embed = discord.Embed(description = f"**LEADERBOARD**", color=0xfaa31e)
        embed.set_image(url="attachment://pil_text.png")
        await ctx.channel.send(file = file,embed=embed)
        
def setup(client):
    client.add_cog(Commands(client))