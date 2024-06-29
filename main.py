import discord
from discord.ext import commands
import os
import asyncio
from utils import TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents, help_command = None)

async def main():
  await load()
  await bot.start(TOKEN)


async def load(): 
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
      try:
        await bot.load_extension(f'cogs.{filename[:-3]}')
        #print((f"- {filename} ✅ "))
      except Exception as e:
        print((f"- {filename} ❌ "))
        print("Failed to load extension {}\n{}: {}".format(filename, type(e).__name__, e))


asyncio.run(main())