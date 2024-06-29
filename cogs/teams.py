import discord
from discord.ext import commands
from utils import react_board, embed_color, aiosqlite 
from cogs.basic import makeQuery

class teamView(discord.ui.View):    

  # initialize the discord.ui.View with a self.bot
  def __init__(self, bot : commands.Bot):
    super().__init__()
    self.bot = bot
    self.makeQuery = makeQuery
  
  @discord.ui.button(label="RED", custom_id="button-red-team", style=discord.ButtonStyle.blurple, emoji='🔴')  
  async def buttonRedTeam_callback(self, interaction, button):
    redRole = discord.utils.get(interaction.user.guild.roles, name="Team Red")
    blueRole = discord.utils.get(interaction.user.guild.roles, name="Team Blu")
    
    if redRole in interaction.user.roles:
      await interaction.user.remove_roles(redRole)
      try: 
        e = await self.makeQuery("UPDATE playerList SET teamID = 'NON' WHERE user = {}".format(interaction.user.id))
        print("Set {} team to NON".format(interaction.user.name))
      except Exception: 
        print("ERR - Couldn't update the team for {}".format(interaction.user.name))
      await interaction.response.send_message("You have left the Red Team", ephemeral=True)
    else: 
      await interaction.user.add_roles(redRole)
      try: 
        e = await self.makeQuery("UPDATE playerList SET teamID = 'RED' WHERE user = {}".format(interaction.user.id))
        print("Set {} team to RED".format(interaction.user.name))
      except Exception:
        print("ERR - Couldn't update the team for {}".format(interaction.user.name))
      if blueRole in interaction.user.roles:
        await interaction.user.remove_roles(blueRole)
      await interaction.response.send_message("You have joined the Red Team!", ephemeral=True)

    
    await self.bot.get_cog("Team").updateEmbed()
  
  @discord.ui.button(label="BLU", custom_id="button-blue-team", style=discord.ButtonStyle.blurple, emoji='🔵')
  async def buttonBluTeam_callback(self, interaction, button):
    redRole = discord.utils.get(interaction.user.guild.roles, name="Team Red")
    blueRole = discord.utils.get(interaction.user.guild.roles, name="Team Blu")

    if blueRole in interaction.user.roles:
      await interaction.user.remove_roles(blueRole)
      try: 
        e = await self.makeQuery("UPDATE playerList SET teamID = 'NON' WHERE user = {}".format(interaction.user.id))
        print("Set {} team to NON".format(interaction.user.name))
      except Exception: 
        print("ERR - Couldn't update the team for {}".format(interaction.user.name))
      await interaction.response.send_message("You have left the Blu Team", ephemeral=True)
    else: 
      await interaction.user.add_roles(blueRole)
      try: 
        e = await self.makeQuery("UPDATE playerList SET teamID = 'BLU' WHERE user = {}".format(interaction.user.id))
        print("Set {} team to BLU".format(interaction.user.name))
      except Exception: 
        print("ERR - Couldn't update the team for {}".format(interaction.user.name))
      if redRole in interaction.user.roles:
        await interaction.user.remove_roles(redRole)
      await interaction.response.send_message("You have joined the Blu Team!", ephemeral=True)
    
    # Call the updateEmbed() function from the Team class
    
    await self.bot.get_cog("Team").updateEmbed()
   
class Team(commands.Cog, name="Team"):  
  
  def __init__(self, bot : commands.Bot):
    self.bot = bot
    self.makeQuery = makeQuery
  global team_message_id

  @commands.Cog.listener("on_ready")
  async def on_ready(self):
    await self.makeQuery("CREATE TABLE IF NOT EXISTS playerList (user INTEGER, username TEXT, teamID TEXT, pts INTEGER)")
    await self.makeQuery("CREATE TABLE IF NOT EXISTS teamScores (team TEXT, score INTEGER)")
    await self.updateDatabase()
    #print("Connected to the teams databases")
  
  async def makeQuery(self, query):
    async with aiosqlite.connect("serverdata.db") as db:
      cursor = await db.cursor()
      await cursor.execute(query)
      result = await cursor.fetchall()
      await db.commit()
      await cursor.close()
      return result
  
  async def updateDatabase(self):
    for member in self.bot.get_all_members():
      if await self.makeQuery(f"SELECT user FROM playerList WHERE user = {member.id}"):
        pass
      else: 
        if member.bot: 
          pass
        else: 
          await self.makeQuery("INSERT INTO playerList VALUES ({}, '{}', 'NON', 0)".format(member.id, member.name))
          print("Added {} to the db".format(member.name))
  
  @commands.command(hidden=True)
  async def tallyPoints(self, team): 
    points = 0
    print("FIX THIS - tallyPoints")
    # Loop through the team members and add their contributions to the points
    query = await self.makeQuery("SELECT * FROM teams WHERE team = '{}'".format(team))
    for member in query: 
      points += member[3]
    return points
  
  @commands.command(name="team")
  async def team(self, ctx : commands.Context, *args):
    print("team command was called - {}".format(args)) 
    if len(args) == 0: # args is None
      # Display the team of the person who called the command
      team = await self.makeQuery("SELECT teamID FROM playerList WHERE user = {}".format(ctx.author.id))
      print("Team of {} is {}".format(ctx.author.name, team[0][0]))
      teamMembers = await self.makeQuery("SELECT username, pts FROM playerList WHERE teamID = '{}'".format(team[0][0]))
      # if the team is NON, tell them so
      if team[0][0] == "NON":
        await ctx.send("You're not on a team! Go hang out in the garden")
      else: 
        # Make a nice embed that displays the team members
        embed = discord.Embed(title="{} Team - Pts".format(team[0][0]), color=embed_color)
        teamList = []
        for member in teamMembers:
          teamList.append("{} - {}".format(member[1], member[0]))
        embed.add_field(name="", value="\n".join(teamList), inline=True)
        await ctx.send(embed=embed)
      print("Printed {}'s team for them".format(ctx.author.name))
    elif (ctx.author.guild_permissions.manage_messages): 
      if 'create' in args or 'setup' in args:
        await ctx.send('Constructing Teams embed. . ')
  
        channel = self.bot.get_channel(react_board)
        await channel.purge(limit=20)
        redTeamArr = []
        bluTeamArr = []
        redTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'RED'")
        bluTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'BLU'")  
        for member in redTeam: 
          redTeamArr.append(member[0])
        for member in bluTeam: 
          bluTeamArr.append(member[0])
        
        embedVar = discord.Embed(title="Choose a Team!", description="", color=embed_color)  
        embedVar.add_field(name=":red_circle: TEAM RED", value="\n".join(redTeamArr), inline=True)
        embedVar.add_field(name=":blue_circle: TEAM BLU", value="\n".join(bluTeamArr), inline=True)
        embedVar.set_footer(text="Press a button to join a team")
        buttonView = teamView(self.bot)
        
        message = await channel.send(embed=embedVar, view=buttonView)
        await ctx.send("Embed created!")
        
        global team_message_id 
        team_message_id = message.id
        #print("Team message ID: {}".format(team_message_id))
        return team_message_id
  
      elif 'balance' in args:
        await ctx.send('Balancing teams. . .')
        #await ctx.send('Particpants: {}')
        print("TODO: Finish balancing teams")
        await ctx.send('Chillophy forgot to finish this command lmao')
  
      elif 'clear' in args:
        await ctx.send('Clearing the teams. . ')
        redRole = discord.utils.get(ctx.guild.roles, name="Team Red")
        blueRole = discord.utils.get(ctx.guild.roles, name="Team Blu")
        #redTeam = await self.makeTQuery("SELECT username FROM playerList WHERE teamID = 'RED'")
        #bluTeam = await self.makeTQuery("SELECT username FROM playerList WHERE teamID = 'BLU'")
        async for member in ctx.guild.fetch_members(limit=None):
          if redRole in member.roles:
            await member.remove_roles(redRole)
          if blueRole in member.roles:
            await member.remove_roles(blueRole)
  
        # Set every user team to NON
        await self.makeQuery(f"UPDATE playerList SET teamID = 'NON'")
        await self.makeQuery("UPDATE teamScores SET score = 0")
        await ctx.send("Teams have been cleared!")
      
      elif 'lock' in args:
        await ctx.send("Locking the teams. . .")
        channel = await self.bot.fetch_channel(react_board)
        await channel.purge(limit=25)
        await ctx.send("Locked!")
        await channel.send("Teams are locked! Good luck everyone!")
      
      else: 
        await ctx.send('Invalid command. Try again.')
    else:
      await ctx.send('?')

  @commands.Cog.listener("updateEmbed")    
  async def updateEmbed(self):
    print("Updating the embed")
    redTeamArr = []
    bluTeamArr = []
    redTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'RED'")
    bluTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'BLU'")  
    for member in redTeam: 
      redTeamArr.append(member[0])
    for member in bluTeam: 
      bluTeamArr.append(member[0])
    message = await self.bot.get_channel(react_board).fetch_message(team_message_id)
    
    embedVar = discord.Embed(title="Team Rosters:", description="", color=embed_color)
    embedVar.add_field(name=":red_circle: TEAM RED", value="\n".join(redTeamArr), inline=True)
    embedVar.add_field(name=":blue_circle: TEAM BLU", value="\n".join(bluTeamArr), inline=True)
    embedVar.set_footer(text="Press a button to join a team")
    await message.edit(embed=embedVar, view=teamView(self.bot))

  
  @commands.command(hidden=True)
  async def printTeam(self, ctx : commands.Context):
    print("Printed the team rosters from db")
    # playerList (user INTEGER, teamID TEXT, pts INTEGER)
    if (ctx.author.guild_permissions.manage_messages):
      redTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'RED'")
      bluTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'BLU'")
      nonTeam = await self.makeQuery("SELECT username FROM playerList WHERE teamID = 'NON'")
      await ctx.send("RED: {}" .format(redTeam))
      await ctx.send("BLU: {}" .format(bluTeam))
      await ctx.send("NON: {}" .format(nonTeam))
    else: 
      await ctx.send("Sorry, you don't have permission to do that.")

async def setup(bot : commands.Bot):
  await bot.add_cog(Team(bot))