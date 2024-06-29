import discord
from discord.ext import commands 
from utils import random
from cogs.basic import makeQuery
#import pydealer

class Blackjack(commands.Cog, name = "Blackjack Cog"):
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    self.makeQuery = makeQuery

  cardSuites = ["♠", "♥", "♦", "♣"]
  cardValues = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
  cardValuesDict = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10} 

  global playerHand, playerSplit, dealerHand, message_id, gameOver, playerWon, embed_desc
  playerHand = []
  playerSplit = [] # To be used only in split cases
  dealerHand = []
  message_id = 0
  gameOver = False
  playerWon = False 
  
  @commands.command(hidden=True)
  async def playGame(self, ctx):
    while not gameOver: 
      await self.sendEmbed(ctx)
      gameOver = await self.checkWinConditions(ctx)
    
    await self.clearHands()
    return playerWon

  async def checkWinConditions(self, ctx): 
    '''
    Blackjack win conditions: 
      - Player has 21, dealer has 21 or player stands and values are equal - Tie
      - Player has 21, dealer has less than 21 - player wins
      - Player has less than 21, dealer has 21 - dealer wins
      - Player has more than 21 - dealer wins
      - Players have less than 21, dealer has more than 21 - player wins
      - Players have less than 21, dealer has less than 21 - game continues
    '''
    try: 
      if (await self.calcValue(playerHand) > 21):
        print("You busted! You lose.")
        return True 
      elif (await self.calcValue(dealerHand) > 21):
        print("Dealer busted! You win.")
        return True
      elif (await self.calcValue(dealerHand) < 21 and await self.calcValue(playerHand) < 21):
        print("No blackjack yet, continue playing.")
        return False 
      # if player has 21 
      elif (await self.calcValue(dealerHand) < 21 and await self.calcValue(playerHand) == 21):
        print("Blackjack! You win!")
        return True 
      elif (await self.calcValue(dealerHand) == 21 and await self.calcValue(playerHand) < 21):
        await ctx.send("Dealer has blackjack! You lose.")
        return True
      else: 
        return False 
    except Exception: 
      await ctx.send("ERR - Couldn't check win conditions")
      return True
  
  async def sendEmbed(self, ctx):
    try: 
      embed = discord.Embed(title = f"Cove Casino | {ctx.author}", description = "")
      embed.add_field(name = "Dealer's Hand:", value = " ".join(dealerHand) + "\nValue: {}".format(await self.calcValue(dealerHand)), inline = True)
      embed.add_field(name = "Your Hand:", value = " ".join(playerHand) + "\nValue: {}".format(await self.calcValue(playerHand)), inline = True)
    except Exception: 
      print("Could not set up embed")
    try: 
      await ctx.send(embed = embed)
    except Exception: 
      print(f"Could not send embed to {ctx.channel}")

  async def dealCard(self, hand): 
    suite = random.choice(self.cardSuites)
    value = random.choice(self.cardValues)
    card = f"{value} {suite}"
    hand.append(card)
    
    
  async def calcValue(self, hand):
    sum = 0
    try: 
      for card in hand: 
        # Determine soft or hard value
        
        
        card = card.split(" ")
        card = card[0]
        cardVal = self.cardValuesDict[card]
        sum = sum + cardVal
      return sum 
    except Exception: 
      print("Had an issue calculating the value of the hand")
      return -1

  async def clearHands(self):
    playerHand.clear()
    playerSplit.clear()
    dealerHand.clear()
    message_id = 0
    gameWon = False 
    
async def setup(bot : commands.Bot):
  await bot.add_cog(Blackjack(bot))