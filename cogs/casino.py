import discord
from discord.ext import commands 
from utils import bot_channel, random, asyncio, currency, maximum_bet, time, embed_color, casino_name
from cogs.basic import makeQuery, isBotChannel

class Casino(commands.Cog, name = "Casino"):
  casinoCooldown = 10
  
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    self.makeQuery = makeQuery
    self.isBotChannel = isBotChannel
    #self.check = check
    
  #@commands.Cog.listener("on_ready")
  #async def on_ready(self):
  #  print("Casino online")
  
  async def addCash(self, ctx, amount : int):
    await ctx.send("Congrats! You won {} {}".format(amount, currency))
    await self.makeQuery("UPDATE econ SET wallet = wallet + {} WHERE user_id = {}".format(amount, ctx.author.id))
    print("Added {} in winnings to {}\'s wallet".format(amount, ctx.author))

  async def removeCash(self, ctx, amount : int):
    await ctx.send("Tough luck! You lost {} {}".format(amount, currency))
    await self.makeQuery("UPDATE econ SET wallet = wallet - {} WHERE user_id = {}".format(amount, ctx.author.id))
    print("Deducted {} in losses to {}\'s wallet".format(amount, ctx.author))

  async def validBet(self, ctx, amount):
    # Check if the user has an account
    try: 
      result = await self.makeQuery("SELECT * FROM econ WHERE user_id = {}".format(ctx.author.id))
      if result: 
        result = result[0]
      else: 
        await ctx.send("Oops, you don't have an account with the bank! !register and try again")
        return False
    except Exception: 
      await ctx.send("ERR - Couldn't get the DB")
      return False

    if amount == "all" or amount == "half":
      #amount = int(result[1] / 2)
      return True 
    if amount is None:
      return await ctx.send("You need to gamble **something**, {}".format(ctx.author.mention))
    else:
      pass
    
    # How can I return the amount and the bool? 
    print(f"Verifying bet of {amount} for {ctx.author}")
    amount = int(amount)
    try: 
      if amount > maximum_bet:
        await ctx.send("You can't bet more than {} {}".format(maximum_bet, currency))
        return False
      elif amount < 1:
        await ctx.send("You can't bet less than 1 {}".format(currency))
        return False
      elif not amount or amount == 0:
        await ctx.send(f"You cant bet nothing, {ctx.author.mention}") 
        return False
      elif amount > result[1]:
        await ctx.send("You can't bet more than what you have in your wallet")
        return False 
      elif amount <= result[1]:
        return True
      else:
        return True
    except Exception: 
      await ctx.send("ERR - Couldn't verify the bet")
      return False

  async def convertToIntBet(self, ctx, amount):
    # For if the player bet "all" or "half"
    userAcc = await self.makeQuery("SELECT wallet FROM econ WHERE user_id = {}".format(ctx.author.id))
    await ctx.send("Gotcha wallet")
    userWallet = userAcc[0][0]
    userWallet = int(userWallet)
    await ctx.send()
    if amount == "all":
      return userWallet
    elif amount == "half":
      return userWallet / 2
    else: # Already an integer
      return amount

  @commands.command(name="chipflip", aliases=["cf"])
  @commands.cooldown(1, casinoCooldown, commands.BucketType.user)
  async def chipflip(self, ctx, choice, bet = None):
    coin = ["Heads", "Tails", "Tails", "Heads", "Tails", "Heads", "Heads", "Tails", "Heads", "Tails"]
    if choice.lower() != "heads" and choice.lower() != "tails" and choice.lower()[0] != "h" and choice.lower()[0] != "t":
      await ctx.send("Please choose either [H]eads or [T]ails")
    
    if await self.isBotChannel(ctx) is True:
      if await self.validBet(ctx, bet) is True:    
        bet = await self.convertToIntBet(ctx, bet)
        await ctx.send("Tossing a chip. . ")
        flip = coin[int(time.time()) % len(coin)]
        #await asyncio.sleep(2)
        await ctx.send(f"The chip landed on {flip}!")
        if choice.lower() == flip.lower() or choice.lower()[0] == flip.lower()[0]:
          await self.addCash(ctx, bet*2)
        else: 
          await self.removeCash(ctx, bet)
      else:
        return await ctx.send("Chip flip cancelled")
    else: 
      return await ctx.send("Let's play in <#{}>".format(bot_channel))
  
  @chipflip.error
  async def chipflip_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can't gamble so often! Try again in {round(error.retry_after)} seconds")
    else:
      await ctx.send("ERR - {}".format(error))

  @commands.command(name="dice", aliases=["roll", "rolldice"])
  @commands.cooldown(1, casinoCooldown, commands.BucketType.user)
  async def dice(self, ctx, dicetype : str = None, choice = None, bet = None):
    await ctx.send(f"You bet {bet} {currency} that the {dicetype} would land on {choice}")
    
    d6 = [1, 2, 3, 4, 5, 6]
    d20 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    mult = 0
    if dicetype == "d6": 
      dice = d6
      mult = 3
    elif dicetype == "d20":
      dice = d20
      mult = 10
    elif not dicetype or dicetype is None: 
      dice = d6 # Default type
    else:
      return await ctx.send("Incorrect die option, please choose [d6] or [d20]")
    max = len(dice) - 1

    try: 
      if bet is None: 
        return await ctx.send("You need to specify an amount to bet")
    except Exception: 
      await ctx.send("ERR - Couldn't determine if amount is None")
    
    try: 
      if not choice: 
        return await ctx.send("You need to pick a number to bet on!")
      elif int(choice) > max or int(choice) < 1:
        return await ctx.send(f"Oops! You need to pick a number between {dice[0]} and {dice[max]}")
    except Exception:  
      return await ctx.send("ERR - Could not verify your dice bet choice")

    if await self.isBotChannel(ctx) is True:
      if await self.validBet(ctx, bet) is True:    
        bet = await self.convertToIntBet(ctx, bet)
        await ctx.send(f"Rolling a {dicetype}, hope for a {choice}!")
        try: 
          roll = dice[int(time.time()) % len(dice)]
        except Exception: 
          return await ctx.send("ERR - Couldn't roll the dice")
        await asyncio.sleep(2)
        await ctx.send(f"The {dicetype} landed on {roll}")
        bet = int(bet)
        if choice == roll:
          await self.addCash(ctx, bet*mult)
        else: 
          await self.removeCash(ctx, bet)
      else: 
        return await ctx.send("Dice roll cancelled")
    else: 
      await ctx.send("Let's play in <#{}>".format(bot_channel))

  @dice.error
  async def dice_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can't gamble so often! Try again in {round(error.retry_after)} seconds") 
    else:
      await ctx.send("ERR - {}".format(error))

  @commands.command(name="slots", aliases=["slot", "spin", "slotmachine"])
  @commands.cooldown(1, 60, commands.BucketType.user)
  async def slots(self, ctx, amount : int = None):
    if (await self.isBotChannel(ctx) is True):
      if (await self.validBet(ctx, amount) is True):  
        amount = await self.convertToIntBet(ctx, amount)
        #user = ctx.author
        slot1 = ["💝", "🎉", "💎", "💵", "💰", "🚀", "🍿"]
        slot2 = ["💝", "🎉", "💎", "💵", "💰", "🚀", "🍿"]
        slot3 = ["💝", "🎉", "💎", "💵", "💰", "🚀", "🍿"]
        sep = " | "
  
        em = discord.Embed( title=casino_name, color=embed_color,
            description=f"```\n"
                        f"| {sep.join(slot1[:3])} |\n"
                        f"| {sep.join(slot2[:3])} | 📍\n"
                        f"| {sep.join(slot3[:3])} |\n"
                        f"```"
        )
        msg = await ctx.reply(content="Spinning. .", embed=em, mention_author=False)
        await asyncio.sleep(3)
  
        total = len(slot1)
        if total % 2 == 0:  # if even
            mid = total / 2
        else:
            mid = (total + 1) // 2
  
        random.shuffle(slot1)
        random.shuffle(slot2)
        random.shuffle(slot3)
        
        result = []
        for x in range(total):
            result.append([slot1[x], slot2[x], slot3[x]])
  
        em = discord.Embed(
            title=casino_name, color=embed_color,
            description=f"```\n"
                        f"| {sep.join(result[mid - 1])} |\n"
                        f"| {sep.join(result[mid])} | 📍\n"
                        f"| {sep.join(result[mid + 1])} |\n"
                        f"```"
        )
  
        slot = result[mid]
        s1 = slot[0]
        s2 = slot[1]
        s3 = slot[2]
        if s1 == s2 == s3:
            reward = round(amount / 2)
            await self.addCash(ctx, amount+reward)
        elif s1 == s2 or s2 == s3 or s1 == s3:
            reward = round(amount / 4)
            await self.addCash(ctx, amount+reward)
        else:
            await self.removeCash(ctx, amount)
        content = "DING DING DING!"
        return await msg.edit(content=content, embed=em)
      else: 
        return await ctx.send("Slots cancelled")
    else: 
      return await ctx.send("Lets play in <#{}>".format(bot_channel))

  @slots.error
  async def slots_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can't gamble so often! Try again in {round(error.retry_after)} seconds")
    else:
      await ctx.send("ERR - {}".format(error))
  
  @commands.command(name="blackjack", aliases=["bj"])
  async def bj(self, ctx, amount : int): 
    if await self.isBotChannel(ctx) is True: 
      if await self.validBet(ctx, amount) is True: 
        bet = await self.convertToIntBet(ctx, bet)
        try: 
          bj_cog = self.bot.get_cog("Blackjack Cog")
          gameWon = await bj_cog.playGame(ctx)
        except Exception: 
          await ctx.send(f"Error during the blackjack game - {Exception}")
          gameWon = False
        if gameWon is True:
          print("Win")
          await self.addCash(ctx, amount*2)
        else: 
          print("Lose")
          await self.removeCash(ctx, amount)
      else: 
        return await ctx.send("Game cancelled")
    else: 
      print("Lets play in <#{}>".format(bot_channel))

  @bj.error
  async def bj_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can't gamble so often! Try again in {round(error.retry_after)} seconds")
    else:
      await ctx.send("ERR - {}".format(error))
  
async def setup(bot : commands.Bot):
  await bot.add_cog(Casino(bot))