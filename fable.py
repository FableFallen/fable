import os
import discord
import asyncio
import openai
import random
import datetime
import pytz
from discord.ext import commands, tasks
import json



intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
token = os.environ.get('BOT_TOKEN')
openai.api_key = os.environ.get('AI_TOKEN')

# Load data from JSON file
with open('data.json', 'r') as f:
    data = json.load(f)

@client.event
async def on_ready():
    global selected_channel
    try:
        # Start the update status task
        selected_channel = discord.utils.get(client.get_all_channels(), id=data['selected_channel'])
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command")
        status_channel = discord.utils.get(client.get_all_channels(), id=1096939868044664923)
        await status_channel.send("Bot is online :green_circle:")
    except Exception as e:
        print(e)

    current_time_utc = datetime.datetime.utcnow()
    est = pytz.timezone('America/New_York')
    current_time_est = current_time_utc.astimezone(est)
    formatted_time = current_time_est.strftime('%A: %I:%M %p | %m/%d/%Y')
    print(f'Bot started at EST: {formatted_time}')

@client.event
async def on_member_join(member):
    # Find the 'Viking' role in the guild
    viking_role = discord.utils.get(member.guild.roles, name="Viking")

    # Check if the 'Viking' role exists
    if viking_role:
        # Assign the 'Viking' role to the new member
        await member.add_roles(viking_role)

@client.tree.command(name="shutdown", description="If you see this command and are not the owner then shame on you person of intrest >:(")
@commands.is_owner()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting Down...", ephemeral=True)
    status_channel = discord.utils.get(client.get_all_channels(), id=1096939868044664923)
    await status_channel.send("Bot shutting down :red_circle:")
    await client.close()

@client.tree.command(name="clear", description="Erases your messages")
@commands.has_role("Administrator")
async def clear(interaction: discord.Interaction, amount: int):
    # Acknowledge the command first
    await interaction.response.defer(ephemeral=True)

    # Delete the messages
    await interaction.channel.purge(limit=amount + 1)

    # Send a follow-up message indicating the number of messages deleted
    await interaction.followup.send(f"{amount} messages deleted.", ephemeral=True)


@client.tree.command(name="cerebral_initiation", description="Sets the channel id for chat bot")
@commands.has_role("Ruler")
async def cerebral_initiation(interaction: discord.Interaction):
    global selected_channel
    selected_channel = interaction.channel

    # Update data
    data['selected_channel'] = selected_channel.id

    # Save data to JSON file
    with open('data.json', 'w') as f:
        json.dump(data, f)

    await interaction.response.send_message(f"AI setup is now active in {selected_channel.mention}. Type any message, and the AI will respond as a normal user.", ephemeral=True)

@client.tree.command(name="cerebral_termination", description="Resets the channel id for chat bot")
@commands.has_any_role("Ruler")
async def cerebral_termination(interaction: discord.Interaction):
    global selected_channel
    selected_channel = None
    await interaction.response.send_message("AI setup is no longer active.", ephemeral=True)


@client.tree.command(name="why_is_roberto_not_online", description="Why Roberto is not online lmao")
@commands.has_role("Ruler")
async def why_is_roberto_not_online(interaction: discord.Interaction):
    prompts = [
        "Generate a story about Roberto being on a thrilling adventure in the Amazon rainforest, with no internet access.",
        "Generate a story about Roberto participating in a week-long meditation retreat where electronic devices are not allowed.",
        "Generate a story about Roberto volunteering in a remote village, helping build infrastructure and unable to access the internet.",
        "Generate a story about Roberto embarking on a spontaneous cross-country road trip, encountering limited internet connectivity.",
        "Generate a story about Roberto getting caught up in a time-travel mishap, leaving him temporarily stranded in the past.",
        "Generate a story about Roberto's internet service provider experiencing a major outage, leaving him without connectivity.",
        "Generate a story about Roberto attending a top-secret conference where all electronic devices must be surrendered upon entry."
    ]
    prompt = random.choice(prompts)
    seed = random.randint(0, 1000000)
    story = generate_text(prompt, seed=seed)
    await interaction.response.send_message(story)

@client.tree.command(name="join_vc", description="WHICH VC DO WE GO! LETS A GO")
@commands.has_any_role("Ruler")
async def join_vc(interaction: discord.Interaction, voice_channel_name: str):
    # Acknowledge the command first
    await interaction.response.defer(ephemeral=True)

    voice_channel = discord.utils.get(interaction.guild.voice_channels, name=voice_channel_name)
    if voice_channel:
        general_channel = discord.utils.get(interaction.guild.text_channels, name="general")
        if general_channel:
            await general_channel.send(f"@everyone Join the '{voice_channel_name}' voice channel immediately!")
            await interaction.followup.send("Announcement sent to the general channel.", ephemeral=True)
        else:
            await interaction.followup.send("The 'general' text channel was not found.", ephemeral=True)
    else:
        await interaction.followup.send("Voice channel not found.", ephemeral=True)


def generate_text(prompt, seed=None):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
        seed=seed,
    )
    return response.choices[0].text

@client.event
async def on_message(message):
    global selected_channel
    if message.author == client.user:
        return
    if message.content.startswith('/'):
        await client.process_commands(message)
    elif message.channel == selected_channel:
        prompt = f"Respond to the following message as an advanced AI: '{message.content}'"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        generated_text = response.choices[0].text.strip()
        await message.channel.send(f"{generated_text}")

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if after.channel.name == "THE OLIGARCHY":
            oligarchy_channel = discord.utils.get(member.guild.text_channels, name="oligarchy")
            ruler_role = discord.utils.get(member.guild.roles, name="Ruler")
            if oligarchy_channel and ruler_role:
                await oligarchy_channel.send(f"{member.mention} joined the 'THE OLIGARCHY' voice channel. {ruler_role.mention}")

client.run(token)
