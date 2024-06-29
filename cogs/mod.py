import discord
from discord.ext import commands
from utils import bot_log, embed_color, datetime 

class Mod(commands.Cog, name="Mod Cog"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot

  @commands.command(aliases=["mute" , "silence"])
  async def void(self, ctx, *args):
    if (ctx.author.guild_permissions.manage_messages):
      if len(args) == 0:
        await ctx.send('Who we voidin\', boss? ')
        await ctx.send('<:byeah:1240385167953104957>')
      else: 
        voidRole = discord.utils.get(ctx.guild.roles, name="Prisoner of the Void")
        user = ctx.message.mentions[0]
        print("Voiding {}".format(user))
        await user.edit(roles=[voidRole])
        await ctx.send('{} has been sent to the shadow realm.'.format(user))
    else: 
      await ctx.send('You need to be a moderator to use this command')

  @commands.command(aliases=["unmute", "devoid", "unsilence"])
  async def free(self, ctx, *args):
    if (ctx.author.guild_permissions.manage_messages):
      if len(args) == 0:
        await ctx.send('You need to specify a user to release from the void')
      else: 
        voidRole = discord.utils.get(ctx.guild.roles, name="Prisoner of the Void")
        user = ctx.message.mentions[0]
        print("DeVoiding {}".format(user))
        await user.remove_roles(voidRole)
        await ctx.send('{} has been released from the void'.format(user))
    else: 
      await ctx.send('You need to be a moderator to use this command')

  @commands.command(aliases=["purge","delete", "del"])
  async def clear(self, ctx, *args):
    if (ctx.author.guild_permissions.manage_messages):
      if len(args) == 0:
        await ctx.send('You need to specify a number of messages to delete')
      else: 
        messagesDel = int(args[0])+1
        delArr = []
        delArr = await ctx.channel.purge(limit=messagesDel)
        await ctx.send('{} message(s) deleted'.format(messagesDel-1))
        
        embed = discord.Embed(title="Messages Purged", color=embed_color)
        embed.add_field(name="{} messages by {} in {}".format(messagesDel, ctx.author, ctx.channel.mention), value="", inline=False)
        try: 
          embed.add_field(name="Messages:", value="\n".join(delArr), inline=False)
        except Exception: 
          print("Couldn't log the messages")
        embed.timestamp = datetime.datetime.utcnow()
        await self.bot.get_channel(bot_log).send(embed=embed)
        print("Purge command called by {}, {} message(s) deleted in {}".format(ctx.author, messagesDel, ctx.channel))

    else: 
      await ctx.send('You need to be a moderator to use this command')
      
  @commands.Cog.listener("on_message_delete")
  async def on_message_delete(self, message):
    if message.author == self.bot.user:
      return
    
    print("A message by {} was deleted in {}".format(message.author, message.channel))
    
    embed = discord.Embed(title="Message Deleted", color=embed_color)
    embed.add_field(name="{} in {}".format(message.author, message.channel.mention), value="", inline=False)
    embed.add_field(name="Message: ", value=message.content, inline=True)
    embed.timestamp = datetime.datetime.utcnow()
    try:
      embed.set_image(url=message.attachments[0].proxy_url)
    except IndexError:
      pass
    
    await self.bot.get_channel(bot_log).send(embed=embed)
  
  @commands.Cog.listener("on_message_edit")
  async def on_message_edit(self, message_before, message_after):
    if message_before.author.bot:
      return
    
    print("A message was modifed by {} in {}".format(message_before.author, message_before.channel))
    embed = discord.Embed(title="Message Edited", color=embed_color)
    embed.add_field(name="{} in {}".format(message_before.author, message_before.channel.mention), value="", inline=False)
    embed.add_field(name="Previous: ", value=message_before.content, inline=True)
    embed.add_field(name="Current: ", value=message_after.content, inline=True)
    embed.timestamp = datetime.datetime.utcnow()
    await self.bot.get_channel(bot_log).send(embed=embed)

async def setup(bot : commands.Bot):
  await bot.add_cog(Mod(bot))