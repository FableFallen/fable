import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.message_content = True

client = commands.Bot(intents=intents)
slash = SlashCommand(client, sync_commands=True)
token = os.environ.get('BOT_TOKEN')

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@slash.slash(name="help",
             description="Shows a list of random commands for testing purposes.",
             options=[
                 create_option(
                     name="command",
                     description="Enter a command name to get specific help",
                     option_type=3,
                     required=False
                 )
             ])
async def _help(ctx: SlashContext, command: str = None):
    if command:
        await ctx.send(f"Help for command {command}: This is a test command.")
    else:
        help_text = """
        - /help: Shows this help message.
        - /example1: An example command.
        - /example2: Another example command.
        - /example3: Yet another example command.
        """
        await ctx.send(help_text)

client.run(token)
