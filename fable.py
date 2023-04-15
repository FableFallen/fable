import os
import discord
from discord.ext import commands
import asyncio
import openai

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
token = os.environ.get('BOT_TOKEN')
openai.api_key = os.environ.get('AI_TOKEN')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

def generate_text(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text

@client.command()
async def WhyisRobertonotonline(ctx):
    # Call the generate_text function with a prompt
    prompt = "Generate a story about why Roberto is not online."
    story = generate_text(prompt)

    # Send the generated story to the Discord channel
    await ctx.send(story)

@client.command(name="joinvc")
@commands.has_role("Ruler")
async def join_vc(ctx, *voice_channel_name: str):
    print(f"Join VC command called with voice_channel_name: {voice_channel_name}")  # Add this line for debugging.
    await ctx.message.delete()
    if not voice_channel_name:
        error_msg = await ctx.send("Voice channel name not provided.")
        await asyncio.sleep(3)
        await error_msg.delete()
        return

    voice_channel_name = " ".join(voice_channel_name)
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=voice_channel_name)
    if voice_channel:
        general_channel = discord.utils.get(ctx.guild.text_channels, name="general")
        if general_channel:
            await general_channel.send(f"@everyone Join the '{voice_channel_name}' voice channel immediately!")
        else:
            await ctx.send("The 'general' text channel was not found.")
    else:
        error_msg = await ctx.send("Voice channel not found.")
        await asyncio.sleep(3)
        await error_msg.delete()



@join_vc.error
async def join_vc_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the 'Ruler' role to use this command.")

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if after.channel.name == "THE OLIGARCHY":
            oligarchy_channel = discord.utils.get(member.guild.text_channels, name="oligarchy")
            ruler_role = discord.utils.get(member.guild.roles, name="Ruler")
            if oligarchy_channel and ruler_role:
                await oligarchy_channel.send(f"{member.mention} joined the 'THE OLIGARCHY' voice channel. {ruler_role.mention}")


client.run(token)

