import discord
from discord.ext import commands
from utils import starboard, starboard_minimum, embed_color, datetime, asyncio, aiosqlite
from cogs.basic import makeQuery

class Starboard(commands.Cog, name="Starboard Cog"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    self.makeQuery = makeQuery
    
  global stars
  stars = ["⭐","🌟","✨","🎇","💫","🌠","🌌"] 
  #         min   5    10   15   20   25    30 stars

  @commands.Cog.listener("on_ready")
  async def on_ready(self):
    # Connect to the database serverdata
    await self.makeQuery("CREATE TABLE IF NOT EXISTS starboard(messageID INTEGER, channelID INTEGER, embedID INTEGER, starCt INTEGER)")
    await self.makeQuery("CREATE TABLE IF NOT EXISTS userStars(userID INTEGER, starsGiven INTEGER, starsReceived INTEGER)")
    await self.updateStarDatabase()
    print("Updated the star database")  

  async def updateStarDatabase(self):
    for member in self.bot.get_all_members():
      if await self.makeQuery(f"SELECT user FROM userStars WHERE user = {member.id}"):
        pass
      else: 
        await self.makeQuery("INSERT INTO userStars VALUES ({}, '0', 0)".format(member.id))
        print("Added {} to the db".format(member.name))      
    
  @commands.command()
  async def star(self, ctx, *args):
    if 'rand' in args or 'random' in args:
      # Pick a random message from the starboard
      return await ctx.send("The star random func is under construction. Check back soon!")
    elif 'lb' in args:
      return await ctx.send("The leaderboard is under construction, check back soon!")
    elif args is None: 
      return await ctx.send("Sorry, but you need to give me more info")
    else:
      return await ctx.send("Sorry, {} is not a feature of the command.".format(args[0]))
  
  async def getStar(self, starCt): 
    if starCt < 5:
      return stars[0]
    elif starCt < 10:
      return stars[1]
    elif starCt < 15:
      return stars[2]
    elif starCt < 20:
      return stars[3]
    elif starCt < 25:
      return stars[4]
    elif starCt < 30:
      return stars[5]
    else:
      return stars[6]

  async def updateUserStars(self, messageAuthor, starGiver):
    # Increment the starsGiven for the payload user
    # Increment the starsEarned for the author of the message
    result = await self.makeQuery("SELECT * FROM starboard WHERE  ")
    message = await self.bot.get_channel(result[1]).fetch_message(result[0])
    
  @commands.Cog.listener("on_raw_reaction_add")
  async def on_raw_reaction_add(self, payload):
    print("{} reacted with {}".format(payload.member, payload.emoji))
    if payload.emoji.name == "⭐":
      message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
      reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
      result = await self.makeQuery("SELECT * FROM starboard WHERE messageID = {}".format(payload.message_id))     
      starCt = reaction.count
      emoji = await self.getStar(starCt)

      # Print the message author and the person who reacted the star
      print("{} was given a star by {}" .format(message.author, payload.member))
      try: 
        await self.makeQuery("UPDATE userStars SET starsGiven = starsGiven + 1 WHERE userID = {}".format(payload.member.id))
        await self.makeQuery("UPDATE userStars SET starsReceived = starsReceived + 1 WHERE userID = {}".format(message.author.id))
        print("Update the user starcounts")
      except Exception: 
        print("Couldn't update the userStars table")
      
      if result:
        # starboard(messageID INTEGER, channelID INTEGER, embedID INTEGER, starCt INTEGER)
        await self.makeQuery("UPDATE starboard SET starCt = {} WHERE messageID = {}".format(starCt, payload.message_id))
        embed = await self.bot.get_channel(starboard).fetch_message(result[2])
        await embed.edit(embed=embed.embeds[0].set_field_at(1, name="", value="{} {}".format(emoji, starCt)))
        print("Edited a starboard embed")
        await self.updateUserStars(messageAuthor, starGiver)
        
      else:
        if (starCt >= starboard_minimum):
          embed = discord.Embed(title="", description=message.jump_url, color=embed_color, url = message.jump_url)
          embed.set_author(name=message.author, icon_url=message.author.avatar.url)
          try: 
            embed.set_image(url=message.attachments[0].url)
          except:
            pass
          embed.add_field(name="", value=message.content, inline=False)
          embed.add_field(name="", value="{} {}".format(emoji, reaction.count), inline=True)
          embed.set_footer(text="Message ID: {}".format(message.id))
          embed.timestamp = datetime.datetime.now()
          embedMessage = await self.bot.get_channel(starboard).send(embed=embed)
          
          await self.makeQuery("INSERT INTO starboard(messageID, channelID, embedID, starCt) VALUES({}, {}, {}, {})".format(payload.message_id, payload.channel_id, embedMessage.id, starCt))
          print("Added a message to the starboard!")
          
        else: 
          pass # message is too low a starCt to be starred
    else: 
      pass
    
  @commands.Cog.listener("on_raw_reaction_remove")
  async def on_raw_reaction_remove(self, payload):
    print("{} unreacted with {}".format(payload.member.name, payload.emoji))
    if payload.emoji.name == "⭐":
      message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
      reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
      starCt = reaction.count
      emoji = await self.getStar(starCt)
      # Check if the message ID is in the database
      result = await self.bot.makeQuery("SELECT * FROM starboard WHERE messageID = {}".format(payload.message_id))
      if result:
        embedID = result[2]
        if (starCt < starboard_minimum or starCt == 0):
          # Delete the message from the database and starboard
          await self.makeQuery("DELETE FROM starboard WHERE messageID = {}".format(payload.message_id))
          embed = await self.bot.get_channel(starboard).fetch_message(embedID)
          await embed.delete()
        else:
          starCt = reaction.count
          emoji = await self.getStar(starCt)
          await self.makeQuery("UPDATE starboard SET starCt = {} WHERE messageID = {}".format(starCt, payload.message_id))
          embed = await self.bot.get_channel(starboard).fetch_message(embedID)
          await embed.edit(embed=embed.embeds[0].set_field_at(1, name="", value="{} {}".format(emoji, starCt)))
          print("Edited a starboard embed")
          
      else:
        print("Message not in database")
        pass
    else: 
      pass

  @commands.command(aliases=["star_db"])
  async def printstarboard(self, ctx):
    if (ctx.author.guild_permissions.manage_messages):
      # Print the database
      async with aiosqlite.connect("serverdata.db") as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM starboard")
        result = await cursor.fetchall()
        await ctx.send(result)
        await cursor.execute("SELECT * FROM userStars")
        result = await cursor.fetchall()
        await ctx.send(result)
    else:
      await ctx.send("You don't have permission to do that")

async def setup(bot : commands.Bot):
  await bot.add_cog(Starboard(bot))