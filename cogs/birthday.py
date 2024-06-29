import discord
from discord.ext import commands 
from cogs.basic import makeQuery

class Birthday(commands.Cog, name = "Birthday Cog"):

  def __init__(self, bot : commands.Bot):
    self.bot = bot 
    self.makeQuery = makeQuery
    
  @commands.Cog.listener("on_ready")
  async def on_ready(self):
    await self.makeQuery("CREATE TABLE IF NOT EXISTS birthday (user_id INTEGER, month INTEGER, day INTEGER)")
    # Call the birthday_check function every day at 09:00
    #await self.bot.loop.create_task(self.birthday_check())

  async def getBirthday(self, user_id):
    print("Fetching birthday for {}".format(user_id))
    birthday = await self.makeQuery("SELECT month, day FROM birthday WHERE user_id = {}".format(user_id))
    if birthday is not None: 
      return birthday
    else: 
      print("No birthday found")
      return None
  
  @commands.command(name="setbirthday", aliases=["setbd"])
  async def addBirthday(self, ctx, date): 
    try: 
      list = date.split("/")
      print(f"Birthday - M {list[0]} - D {list[1]}")
      
      await ctx.send("Recording birthday as ({}/{})".format(list[0], list[1]))
      month = int(list[0])
      day = int(list[1])
      if month in (1, 3, 5, 7, 8, 10, 12):
        if day > 31 or day < 1:
          return await ctx.send("Invalid day.")
        else:
          pass
      elif month in (4, 6, 9, 11):
        if day > 30 or day < 1:
          return await ctx.send("Invalid day.")
        else:
          pass
      elif month == 2:
        if day > 29 or day < 1:
          return await ctx.send("Invalid day.")
        else:
          pass
      else:
          return await ctx.send("Invalid month.")
    
      # If the birthday is already in the database, update it
      if await self.getBirthday(ctx.author.id):
        await self.makeQuery("UPDATE birthday SET month = {}, day = {} WHERE user_id = {}".format(month, day, ctx.author.id))
        await ctx.send("Birthday updated.")
      else:
        await self.makeQuery("INSERT INTO birthday VALUES ({}, {}, {})".format(ctx.author.id, list[0], list[1]))
        await ctx.send("Birthday added.")

    except Exception:
      return await ctx.send("Format Error - Please use MM/DD")

  @commands.command(name="birthday", aliases=["bd"])
  async def birthday(self, ctx, member : discord.Member):
    birthday = await self.getBirthday(member.id)
    print("Fetched birthday.")
    if birthday is not None:
      await ctx.send("Birthday of {} is {}/{}".format(member.name, birthday[0], birthday[1]))
    else:
      await ctx.send("No birthday found for {}".format(member.name))
  
  @commands.command(aliases=["bddb"])
  async def birthdaydb(self, ctx):
    if (ctx.author.guild_permissions.manage_messages):
      await ctx.send("Printing birthday database")
      info = await self.makeQuery("SELECT * FROM birthday")
      if info is not None:
        await ctx.send(info)
      else:
        await ctx.send("No data in the database")
    else: 
      await ctx.send("You don't have the permissions to do that!")

  
async def setup(bot : commands.Bot):
  await bot.add_cog(Birthday(bot))