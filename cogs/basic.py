import discord
from discord.ext import commands 
from utils import aiosqlite, asyncio, random, bot_channel, announce_channel

@staticmethod
async def makeQuery(query):
  async with aiosqlite.connect("serverdata.db") as db:
    cursor = await db.cursor()
    await cursor.execute(query)
    result = await cursor.fetchall()
    await db.commit()
    await cursor.close()
  await db.close()
  return result

@staticmethod
async def isBotChannel(ctx):
  if (ctx.channel.id == bot_channel):
    return True
  else: 
    return True

class Basic(commands.Cog, name = "Basic Cog"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    
  @commands.Cog.listener("on_ready")
  async def on_ready(self):
    print("Logged in as {}".format(self.bot.user))
    await self.keepselfAwake()

  async def keepselfAwake(self):
    spamSelf = 1247294196348489808 
      
  @commands.Cog.listener("on_join")
  async def on_member_join(self, member):
    await self.bot.get_channel(announce_channel).send("Welcome to the server, {}".format(member.mention))

  @commands.Cog.listener("on_message")
  async def mentioned(self, message):
    if message.author == self:
      return
    
    pinged = ["Ponged", "What?", "Absolutely UNACCEPTABLE! I cannot begin to comprehend why you just pinged me on the Discord app. It seems the divide between you and I (on intellectual levels) is greater than I could have ever imagined. While I was busy creating the next big thing, you and your underdeveloped brain decided to humor me with “comedy gold,” as others have said recently. Well, you certainly have failed to humor me — in fact, you have actually made me quite upset. It is for that I applaud you, I truly do. You may have just been the first of the cesspool of commoners to finally pique my attention, the first whose utter stupidity has finally caught the interest of a higher being. Well, I’m listening. What is it today, “Funnyman?” Is it another mediocre meme? Another “le epic copypasta?” This is the first and last time I acknowledge a Funnyman. In fact, this is the last time any Funnyman will be acknowledged. Image permissions will be removed starting immediately, and a one minute slow mode is being enacted in that very moment. You’ve done God’s work, Funnyman. You finally broke the last straw and ruined it for everyone else. I grow gleeful at just the thought of you writhing in pain the next time you go to shitpost, realizing quickly that this liberty is no more; know it is not a liberty, it is an act of insubordination, treason, terrorism. ", "Hello! (^-^_)/", "I'm here!", "Ping!", "G'Day Friend!", "Hello, I'm a bot!", "I'm a bot!", "I'm a bot", "Can I help you?", "I'm here to help!", "I'm here to help!", "I'm here to help you!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", "Hi there!", '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>', '<:ping:1240385681558339728>' ]
    owner_id = 538154305983741972
    # if the owner is messaged, reply with a random message from the list
    if f"<@!{owner_id}>" in message.content:
      print("Owner pinged!")
      await message.channel.send(random.choice(pinged))
      
    # if the message is a ping, reply with a random message from the pinged list
    if self.bot.user.mentioned_in(message):
      if message.author == self.bot.user:
        return
      else:   
        await message.reply("{}".format(random.choice(pinged)))
       
  @commands.command(name='reload', hidden=True)
  async def reload(self, ctx, *, module : str = None):
    """Reloads a module."""
    try:
      await self.bot.reload_extension(f"cogs.{module}")
      await ctx.send(f"Reloaded {module} cog")
      print(f"Reloaded the {module} cog")
    except Exception as e:
      await ctx.send(f"Failed to reload the {module} cog")
      print(f"Couldn't reload the {module} cog")
    
    #else:
    
async def setup(bot : commands.Bot):
  await bot.add_cog(Basic(bot))