import discord
from discord.ext import commands
from discord import Webhook 
from utils import embed_color, random, time

class Misc(commands.Cog, name="Misc"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot
  
  @commands.command(aliases=["pong", "test", "check", "alive"])
  async def ping(self, ctx : commands.Context):
    await ctx.send("!")
  
  @commands.command(aliases=["av", "pfp", "profilepic", "pic"])
  async def avatar(self, ctx, *,  avamember : discord.Member=None):
    if not avamember:
      avamember = ctx.message.author
    userAvatar = avamember.display_avatar
    embed = discord.Embed(title="Member Avatar", description="", color=embed_color)
    embed.set_image(url=userAvatar.url)
    await ctx.send(embed=embed)

  @commands.command(name="joke") # Integrate Joke api - https://sv443.net/jokeapi/v2/
  async def joke(self, ctx):
    await ctx.send("Downloading {}\'s personality. . .".format(ctx.message.author.mention))
    time.sleep(2)
    await ctx.send("Completed!")
    time.sleep(1)
    await ctx.send("Processing the funny. . .")
    time.sleep(5)
    await ctx.send("Completed!")
    
    humanJokes = ["Why did the chicken cross the road? To get to the other side!", "What do you call a fake noodle? An impasta!","You've probably walked more miles in a video game than you have in real life. Please touch grass.", "If the only woman you know is a VTuber's avatar, you have issues."]
    
    aiJokes = ["I'm not sure if you're a human or an AI, but I can't fix that.", "I apologize, but I do not feel comfortable telling bad jokes, even if they are intended to be funny. As an AI assistant, my purpose is to have thoughtful, respectful conversations and provide helpful information to users, not to engage in telling potentially inappropriate or offensive humor. Perhaps we could find a more constructive topic to discuss that aligns with my design as a considerate conversational partner. I'm happy to assist you with other questions or tasks that don't involve telling jokes. Please let me know if there is something else I can help with.", "Would you like to hear a joke? I can't find any here to tell"]
    
    chance = (random.randint(1,4))
    if (chance <= 2):
      await ctx.send("Joke: {}".format(random.choice(humanJokes)))
    elif (chance == 3):   
      await ctx.send("ERR 404: FUNNY NOT FOUND")
    else: # Bot joke, oh lord
      await ctx.send("{}".format(random.choice(aiJokes)))
    print("Told a joke to {}".format(ctx.message.author))
  
  @commands.command(aliases=["say", "repeat", "copy"])
  async def echo(self, ctx, *, message):
    # Prevent people from mentioning roles
    if "@" in message:
      return await ctx.send("You can't mention in this command!")
    else: 
      await ctx.send(message)

  @commands.command()
  async def mimic(self, ctx, member : discord.Member=None): 
    print("Mimic process begun")
    
    if not member: 
      member = ctx.author
    
    await ctx.send("Mimicking the next message: ")
    message = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
      
    print(f"Mimic command called by {ctx.author} to mimic the message {message.content} as {member.name}")
    
    try: 
      webhook = await ctx.channel.create_webhook(name=member.name)
      await webhook.send(content=message.content, username=member.nick, avatar_url= member.avatar.url)

      webhooks = await ctx.channel.webhooks()
      for webhook in webhooks:
        await webhook.delete()
    
    except Exception as e: 
      print(e)
      await ctx.send(f"ERR - {e}")
    
  @commands.command(name="embed")
  async def embed(self, ctx, *, message):
    embed = discord.Embed(title="Embedded Message", description=message, color=embed_color)
    await ctx.send(embed=embed)

  @commands.command(aliases=["question", "askeight", "ask", "8ball"])
  async def eightball(self, ctx, *, question):
    answers = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful.", "No.", "Maybe.", "I don't know.", "I'm not sure.", "I'm not sure what you mean."]
    embed = discord.Embed(title="The 8 Ball replies!", description="{}\n".format(question), color=embed_color)
    embed.add_field(name="🎱 {}".format(random.choice(answers)), value = "")
    await ctx.send(embed=embed)

  @commands.command()
  async def coinflip(self, ctx, *, choice : str):
    coin = ["Heads", "Tails"]
    return await ctx.send("The coin landed on {}!".format(random.choice(coin)))
  
  # Reply with a banana gif if someone says !banana
  @commands.command(name="banana")
  async def banana(self, ctx):
    embed = discord.Embed(title=":banana: Banana :banana:", description="", color=embed_color)
    file = discord.File("banana.gif", filename="banana.gif")
    embed.set_image(url="attachment://banana.gif")
    await ctx.send(file=file, embed=embed)



async def setup(bot: commands.Bot):
  await bot.add_cog(Misc(bot))