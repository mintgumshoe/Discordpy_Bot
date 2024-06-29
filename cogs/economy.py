import discord
from discord.app_commands.checks import has_permissions
from discord.ext import commands 
from utils import bot_channel, embed_color, currency, random 
from cogs.basic import isBotChannel, makeQuery

class Economy(commands.Cog, name = "Economy"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    self.makeQuery = makeQuery
    self.isBotChannel = isBotChannel
  
  @commands.Cog.listener("on_ready")
  async def on_ready(self):
    await self.makeQuery("CREATE TABLE IF NOT EXISTS econ (user_id INTEGER, wallet INTEGER, bank INTEGER)")
    await self.makeQuery("CREATE TABLE IF NOT EXISTS inventory (user_id INTEGER, item_name TEXT, item_description TEXT)")
    await self.makeQuery("CREATE TABLE IF NOT EXISTS items (item_name TEXT, item_price INTEGER, item_description TEXT, item_message TEXT, role_given_id TEXT, role_removed_id TEXT)")
  
  ##########################################################################################################
                                                  # Bank # 
  @commands.command(name="open_account", aliases=["register", "create_account", "create"])
  async def open_account(self, ctx : commands.Context):
    result = await self.makeQuery("SELECT user_id FROM econ WHERE user_id = {}".format(ctx.author.id))
    if result is None:
      await self.makeQuery("INSERT INTO econ (user_id, wallet, bank) VALUES ({}, {}, {})".format(ctx.author.id, 0, 100))
      await ctx.send("Congratulations, you've registered an account with Cove Credit Union! \nAs a reward, you've been given 100 {} to start with!".format(currency))
    else:
      await ctx.send("You already have an account!")

  @commands.command(name="balance", aliases=["bal", "acc", "account", "bank", "money", "cash"])
  async def balance(self, ctx, member : discord.Member = None):
    if member is None:
      member = ctx.author
    if await self.isBotChannel(ctx) is True:
      #print(f"Fetching the account of {member.name}")
      result = await self.makeQuery("SELECT * FROM econ WHERE user_id = {}".format(member.id))
      account = result[0]
      #print(f"Account fetched! W: {account[1]}, B: {account[2]}")
      if result: 
        try: 
          embed = discord.Embed(title="🏛️ Cove Credit Union", description=f"{member}'s account")
          embed.add_field(name="👛 Wallet", value=f"{account[1]}", inline=False)
          embed.add_field(name="💰 Bank ", value=f"{account[2]}", inline=False)
          return await ctx.send(embed=embed)
        except Exception: 
          print("Could not send the embed")
          return await ctx.send("Oops! Our bank is having issues right now. Please try again later.")
      else: 
        return await ctx.send(f"I cant find our account with {member.name}. !register and try again")
    else: 
      return await ctx.send("Let's bank in <#{}>".format(bot_channel))

  @commands.command(name="deposit", aliases=["dep"])
  async def deposit(self, ctx, amount = None):
    print("Attempting to deposit {} for {}".format(amount, ctx.author.name))
    if amount is None:
      return await ctx.send("Please specify an amount to deposit")
    if await self.isBotChannel(ctx) is True:
      result = await self.makeQuery(f"SELECT * FROM econ WHERE user_id = {ctx.author.id}")
      account = result[0]
      if (amount.isnumeric()) or (amount.isdigit()):
        amount = int(amount)
        if amount <= 0:
          return await ctx.send("You can't deposit negative amounts!")
        elif amount > account[1]:
          return await ctx.send("You can't deposit more than what is in your wallet")
      elif isinstance(amount, str) is True:
        if amount == "all":
          amount = account[1]
        elif amount == "half":
          amount = account[1] / 2
      else: 
        return await ctx.send("ERR - please specify a number or half/all")
      try: 
        await self.makeQuery(f"UPDATE econ SET bank = bank + {amount} WHERE user_id = {ctx.author.id}")
        await self.makeQuery(f"UPDATE econ SET wallet = wallet - {amount} WHERE user_id = {ctx.author.id}")
        return await ctx.send("Deposited {} {}".format(amount, currency))
      except Exception: 
        await ctx.send("ERR - Could not complete the transaction")
    else: 
      return await ctx.send("Let's bank in <#{}>".format(bot_channel))    
      
  @commands.command(name="withdraw", aliases=["with"])
  async def withdraw(self, ctx, amount = None):
    print("Attempting to withdraw {} for {}".format(amount, ctx.author.name))
    if amount is None:
      return await ctx.send("Please specify a numerical amount to withdraw")
    if await self.isBotChannel(ctx) is True:
      result = await self.makeQuery(f"SELECT * FROM econ WHERE user_id = {ctx.author.id}")
      account = result[0]
      if (amount.isnumeric()) or (amount.isdigit()):
        amount = int(amount)
        if amount <= 0:
          return await ctx.send("You can't withdraw negative amounts!")
        elif amount > account[2]:
          return await ctx.send("You can't withdraw more than what is in your bank")
      elif isinstance(amount, str) is True:
        if amount == "all":
          amount = account[2]
        elif amount == "half":
          amount = account[2] / 2
      else: 
        return await ctx.send("ERR - please specify a number or half/all")
      try: 
        await self.makeQuery(f"UPDATE econ SET bank = bank - {amount} WHERE user_id = {ctx.author.id}")
        await self.makeQuery(f"UPDATE econ SET wallet = wallet + {amount} WHERE user_id = {ctx.author.id}")
        return await ctx.send("Withdrew {} {}".format(amount, currency))
      except Exception: 
        await ctx.send("ERR - Could not complete the transaction")
    else: 
      return await ctx.send("Let's bank in <#{}>".format(bot_channel))  
  
  @commands.command(name="send", aliases=["give", "gift"]) # Wallet to wallet
  async def send(self, ctx, member : discord.Member, amount = None):
    if not member:
      return await ctx.send("You need to specify someone to give the money to!")
    elif member.id == ctx.author.id:
      return await ctx.send("You cannot send money to yourself!")
    if amount is None: 
      return await ctx.send("You need to specify an amount to give!")
    
    result = await self.makeQuery("SELECT wallet FROM econ WHERE user_id = {}".format(ctx.author.id))
    if result:
      if amount > result[0]:
        await ctx.send("You don't have that much money!")
      else: 
        await self.makeQuery("UPDATE econ SET wallet = wallet - {} WHERE user_id = {}".format(amount, ctx.author.id))
        await self.makeQuery("UPDATE econ SET wallet = wallet + {} WHERE user_id = {}".format(amount, member.id))
        await ctx.send("You gave {}, {} {} from your wallet.".format(member.name, amount, currency))
    
  @commands.command(aliases=["trans", "wire"]) # Bank to bank
  async def transfer(self, ctx, member : discord.Member, amount = None):
    if not member:
      return await ctx.send("You need to designate an account to transfer to!")
    elif member == ctx.author:
      return await ctx.send("You can't transfer money to yourself!")
    if amount is None:
      return await ctx.send("You need to give me an amount to transfer")
    
    result = await self.makeQuery("SELECT bank FROM econ WHERE user_id = {}".format(ctx.author.id))
    if result:
      if amount > result[0]:
        await ctx.send("You don't have that much money!")
      else: 
        await self.makeEconQuery("UPDATE econ SET bank = bank - {} WHERE user_id = {}".format(amount, ctx.author.id))
        await self.makeEconQuery("UPDATE econ SET bank = bank + {} WHERE user_id = {}".format(amount, member.id))
        await ctx.send("You wired {} {} from your account to {}\'s ".format(amount, currency, member.name))
    else: 
      await ctx.send("You don't have an account!")
   
  @commands.command(name="steal", aliases=["rob", "mug"]) # Rob the other person's wallet
  async def steal(self, ctx, member : discord.Member):
    if not member:
      member = ctx.author
    if member == ctx.author:
      return await ctx.send(f"You can't steal from yourself, {ctx.author.name}!")
    else: 
      thief = await self.makeQuery("SELECT wallet FROM econ WHERE user_id = {}".format(ctx.author.id))
      if thief: 
        result = await self.makeQuery("SELECT wallet FROM econ WHERE user_id = {}".format(member.id))
        if result:
          if result[0] < 100:
            await ctx.send("{} doesn't have enough money on hand to rob!".format(member.name))
          else: 
            await self.makeQuery("UPDATE econ SET wallet = wallet - {} WHERE user_id = {}".format(100, member.id))
            await self.makeQuery("UPDATE econ SET wallet = wallet + {} WHERE user_id = {}".format(100, ctx.author.id))
            await ctx.send("You stole {} {} from {}'s account".format(100, currency, member.name))
        else: 
          return await ctx.send("{} doesn't have a wallet!".format(member.name))
      else: 
        return await ctx.send("You can't really steal if you dont have a wallet to put it in")

  @commands.command(name="work", aliases=["job", "career"])
  @commands.cooldown(1, 3600, commands.BucketType.user)
  async def work(self, ctx):
    job_pay = [["Banker", 200], ["Doctor", 500], ["Lawyer", 400], ["Teacher", 300], ["Cashier", 200], ["Janitor", 100], ["Waiter", 200], ["Bartender", 100], ["Actor", 100], ["Garbage Man", 200]]

    
    userWallet = await self.makeQuery(f"SELECT wallet FROM econ WHERE user_id = {ctx.author.id}")
    if userWallet: 
      job = random.choice(job_pay)
      await ctx.send(f"You worked as a {job[0]} for the hour and earned {job[1]} {currency}")
      try: 
        await self.makeQuery(f"UPDATE econ SET wallet = wallet + {job[1]} WHERE user_id = {ctx.author.id}")
      except Exception:
        await ctx.send("An error occured while adding your pay to your wallet.")
        print(f"Failed to add {job[1]} to {ctx.author.name}\'s wallet {Exception}")
    else: 
      await ctx.send("You need a bank account and wallet to deposit into first!")

  @work.error
  async def work_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can only work once an hour! Try again in {round(error.retry_after/60)} minutes")
    else:
      await ctx.send("ERR - {}".format(error))
      
  @commands.command(name="beg", aliases=["plead"])
  @commands.cooldown(1, 1300, commands.BucketType.user)
  async def beg(self, ctx):
    beggar = await self.makeQuery(f"SELECT wallet FROM econ WHERE user_id = {ctx.author.id}")
    if beggar: 
      failChance = random.randint(1, 100)
      amount = random.randint(1, 50)
      if failChance != random.randint(1, 100): # If the 2 d100s do not match up
        await self.makeQuery(f"UPDATE econ SET wallet = wallet + {amount} WHERE user_id = {ctx.author.id}")
        await ctx.send("You begged and received {} {}".format(amount, currency))
      else: 
        wallet = await self.makeQuery(f"SELECT wallet FROM econ WHERE user_id = {ctx.author.id}")
        if wallet[0] <= 0:
          await ctx.send("You begged a robber, but they couldn't take anything, you're that broke!")
        else: 
          randRob = random.randint(1, wallet[0])
          await ctx.send("Tough Luck! You begged a robber and got robbed for {} {}".format(randRob, currency))
          await self.makeQuery(f"UPDATE econ SET wallet = wallet - {randRob} WHERE user_id = {ctx.author.id}")
    else: 
      await ctx.send("You need a wallet to store your cash in. !register and try again")

  @beg.error
  async def beg_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can only beg once an hour! Try again in {round(error.retry_after/60)} minutes")
    else:
      await ctx.send("ERR - {}".format(error))
  
  @commands.command(name="daily")
  @commands.cooldown(1, 86400, commands.BucketType.user)
  async def daily(self, ctx):
    userWallet = await self.makeQuery(f"SELECT wallet FROM econ WHERE user_id = {ctx.author.id}")
    if userWallet:
      await self.makeQuery(f"UPDATE econ SET wallet = wallet + {500} WHERE user_id = {ctx.author.id}")
      await ctx.send("You claimed your daily reward of 500 {}!".format(currency))
    else: 
      await ctx.send("You need a wallet to store your cash in. !register and try again tomorrow")

  @daily.error
  async def daily_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.reply(f"You can only claim your daily once a day! Try again in {round(error.retry_after/3600)} hours")
    else:
      await ctx.send("ERR - {}".format(error))

  ##########################################################################################################
                                            # Commerce #
  @commands.command(name="inventory", aliases=["inv", "hotbar", "ledger"])
  async def inventory(self, ctx):
    invQuery = await self.makeQuery("SELECT * FROM inventory WHERE user_id = {}".format(ctx.author.id))
    embed = discord.Embed(title="{}\'s inventory".format(ctx.author.name), description="", color=embed_color)
    print(f"{ctx.author.name}'s inventory: \n {invQuery}")
    
    if invQuery is None or not invQuery: 
      embed.add_field(name="", value="Your inventory is empty")
    else: 
      try:
        num = 1
        for item in invQuery: 
          embed.add_field(name=f"{num}: {item[1]}", value=f"{item[2]}", inline=False)
          num = num + 1
      except Exception:
        return await ctx.send("I couldn't load your inventory!")
    embed.set_footer(text="!buy some items in the !shop so you can !use them")
    await ctx.send(embed=embed)
    print(f"Printed inventory for {ctx.author.name}")

  @commands.command(name="shop", aliases=["store", "market"])
  async def shop(self, ctx):
    shopQuery = await self.makeQuery("SELECT * FROM items")
    embed = discord.Embed(title="== Coconut Mall ==", description="!buy items here", color=embed_color)
    if shopQuery is None or not shopQuery: 
      embed.add_field(name="No items in the shop", value="Check back later!")
    else: 
      try:
        num = 1
        for item in shopQuery: 
          embed.add_field(name=f"{num}: {item[0]} - {item[1]} {currency}", value=f"{item[2]}", inline=False)
          num = num + 1
      except Exception:
        return await ctx.send("I couldn't load the shop items!")
    await ctx.send(embed=embed)
 
  @commands.command(name="buy", aliases=["purchase", "acquire"])
  async def buy(self, ctx, item = None):
    print(f"Buying {item} for {ctx.author}")
    if item is None:
      return await ctx.send("You need to specify an item to buy")
    else:
      item = item.lower()

      try: 
        wallet = await self.makeQuery(f"SELECT wallet FROM econ WHERE user_id = {ctx.author.id}")
        wallet = wallet[0][0]
      except Exception: 
        return await ctx.send("I had trouble fetching your wallet information")

      try: 
        # shop (item_name TEXT, item_price INTEGER, item_description TEXT)")
        if item.isnumeric():
          shopList = await self.makeQuery("SELECT * FROM shop")
          item = shopList[int(item) - 1]
        else: 
          shopItem = await self.makeQuery(f"SELECT * FROM shop WHERE item_name = '{item}'")
          item = shopItem[0]
        price = item[1]
      except Exception: 
        return await ctx.send("I had trouble fetching the item's information")

      '''
      # Pull the member's inventory and check they dont have the item already
      invQuery = await self.makeQuery(f"SELECT * FROM inventory WHERE user_id = {ctx.author.id}")
      inventory = invQuery[0]
      if invQuery is None or not invQuery:
        return await ctx.send(f"I could not fetch your inventory.")
      elif item[0] in inventory: 
        return await ctx.send(f"You already own {item[0]}!")
      else: 
        pass
      '''
      
      try: 
        if wallet:
          if wallet < price:
            return await ctx.send(f"You don't have enough money to purchase the {item[0]}")
          else: 
            await self.makeQuery(f"INSERT INTO inventory (user_id, item_name, item_description) VALUES ({ctx.author.id}, '{item[0]}', '{item[2]}')")
            await self.makeQuery(f"UPDATE econ SET wallet = wallet - {price} WHERE user_id = {ctx.author.id}")
            return await ctx.send(f"You bought {item[0]} for {price} {currency}")
        else:
         return await ctx.send("You need to !register to get an account first!") 
      except Exception: 
        return await ctx.send("I had trouble verifying your wallet")
  
  ##########################################################################################################
                                              # Admin # 
  @commands.command(aliases=["addbal", "addmoney", "addcredit"])
  async def addBal(self, ctx, member : discord.Member, amount : int):
    # If no member given, its the author
    if not member:
      member = ctx.author
    if (ctx.author.guild_permissions.manage_messages):
      await self.makeQuery("UPDATE econ SET bank = bank + {} WHERE user_id = {}".format(amount, member.id))
      await ctx.send("Added {} {} to {}'s account".format(amount, currency, member.name))
    else: 
      await ctx.send("You don't have the permissions to do that!")
   
  @commands.command(aliases=["removebal", "removecredit", "removemoney"])
  async def removeBal(self, ctx, member : discord.Member, amount : int):
    # If no member given, its the author
    if not member:
      member = ctx.author
    if (ctx.author.guild_permissions.manage_messages):
      await self.makeQuery("UPDATE econ SET bank = bank - {} WHERE user_id = {}".format(amount, member.id))
      await ctx.send("Removed {} {} from {}'s account".format(amount, currency, member.name))
    else: 
      await ctx.send("You don't have the permissions to do that!")
  
  @commands.command(name="bug_bounty", aliases=["bbounty", "bugbounty"])
  async def bug_bounty(self, ctx, member : discord.Member):
    await self.addBal(ctx, member, 100)
    await ctx.send("Bug Bounty rewarded to {}".format(member.name))

  @commands.command(name="iteminfo", aliases=["info", "item_info"])
  async def iteminfo(self, ctx, item = None):
    if item is None:
      return await ctx.send("You need to specify an item to look up")
    else:
      item = item.lower()
      try: 
        itemQuery = await self.makeQuery(f"SELECT * FROM shop WHERE item_name = '{item}'")
        item = itemQuery[0]
      except Exception: 
        return await ctx.send("I couldn't find that item")
      
      try: 
        embed = discord.Embed(title=f"Item Information - {item[0]}", description="", color=embed_color)
        embed.add_field(name="Name", value=f"{item[0]}", inline=False)
        embed.add_field(name="Price", value=f"{item[1]} {currency}", inline=False)
        embed.add_field(name="Description", value=f"{item[2]}", inline=False)
        embed.add_field(name="Message", value=f"{item[3]}", inline=False)
      except Exception: 
        return await ctx.send("Could not load the item's information")
      try: 
        await ctx.send(embed=embed)
      except Exception: 
        return await ctx.send("Couldn't send the information")

  @commands.command(name="itemsetup", aliases=["setupitem", "item_setup"])
  async def itemsetup(self, ctx, func = None): 
    if (ctx.author.guild_permissions.manage_messages):
      if func == "add":
        await self.additem(ctx)
      elif func == "edit": 
        await self.edititem(ctx)
      elif func == "remove":
        await self.removeitem(ctx)
      else:
        return await ctx.send("ERR - Invalid function")
    else: 
      return await ctx.send("You don't have the permissions to do that!")

  ##########################################################################################################
                                            # Item Setup #  
  async def check(ctx):
    return ctx.author.guild_permissions.manage_messages

  '''
    await ctx.send("Type the message you'd like me to repeat")
    message = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
    await ctx.send(message.content)
  '''
  
  async def additem(self, ctx):
    # take in the item name, price, description, and message
    try: 
      await ctx.send("First, tell me the name of the item")
      item_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      await ctx.send("Now, give me a short description of the item")
      item_description = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      await ctx.send("What should I say when the item is used? ")
      item_message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      await ctx.send("Now, do we add a role with this item? Ping that role, or say none to skip")  
      item_role_given = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      try: 
        role_given_id = discord.utils.get(ctx.user.guild.roles, name=item_role_given.content)
        await ctx.send(f"Located role with id of {role_given_id}")
      except Exception as e: 
        await ctx.send("Couldn't locate that role")
      await ctx.send("Now, do we remove a role with this item? Ping that role, or say none to skip")  
      item_role_removed = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      await ctx.send("Finally, let's set a price for the item")
      item_price = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
    except Exception: 
      return await ctx.send("Oops! I ran into an error while collecting item information. Please try again later")

    
    await ctx.send(f"Adding item {item_name.content} to the item list at a price {item_price.content} with the description of {item_description.content}. It will add the role {item_role_given.content} and remove the role {item_role_removed.content}") 
    
    if item_role_given.content.lower() == "none":
      item_role_given = None 
    if item_role_removed.content.lower() == "none":
      item_role_removed = None 
      
    try: 
      # items (item_name TEXT, item_price INTEGER, item_description TEXT, item_message TEXT, role_given_id TEXT, role_removed_id TEXT)
      await self.makeQuery(f"INSERT INTO items (item_name TEXT, item_price INTEGER, item_description TEXT, item_message TEXT, role_given_id TEXT, role_removed_id TEXT) VALUES ('{item_name.content}', '{item_price.content}', '{item_description.content}', '{item_message.content}', '{item_role_given.content}', '{item_role_removed.content}')") 
      return await ctx.send("Added the item successfully")
    except Exception:
      return await ctx.send("I had trouble adding the item to the shop")
  
  async def removeitem(self, ctx):
    item_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)  
    await self.makeQuery("DELETE FROM shop WHERE item_name = \"{}\"".format(item_name))
    return await ctx.send("Removed {} from the shop".format(item_name))
    
  async def edititem(self, ctx):
    return await ctx.send("This command isnt done yet, lol")
    
  ##########################################################################################################
                                            # View DB #
  @commands.command(name="printitems")
  async def printitems(self, ctx):
    if (ctx.author.guild_permissions.manage_messages):
      await ctx.send("Printing the database")
      info = await self.makeQuery("SELECT * FROM items")
      print(info)
      if info is not None:
        await ctx.send(info)
      else:
        await ctx.send("No data in the database")
    else: 
      await ctx.send("You don't have the permissions to do that!")

  @commands.command(aliases=["econ_db"])
  async def printecon(self, ctx):
    if (ctx.author.guild_permissions.manage_messages):
      await ctx.send("Printing the database")
      info = await self.makeQuery("SELECT * FROM econ")
      print(info)
      if info is not None:
        await ctx.send(info)
      else:
        await ctx.send("No data in the database")
    else: 
      await ctx.send("You don't have the permissions to do that!")

  ##########################################################################################################

async def setup(bot : commands.Bot):
  await bot.add_cog(Economy(bot))