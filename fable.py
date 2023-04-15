import os
import discord
import asyncio
import openai
import random
import datetime
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
intents.message_content = True

client = commands.Bot(intents=intents)
slash = SlashCommand(client, sync_commands=True)
token=os.environ.get('BOT_TOKEN')
openai.api_key = os.environ.get('AI_TOKEN')
selected_channel = None

@client.event
async def on_ready():
    current_time = datetime.datetime.utcnow().strftime('%A @ %I:%M %p')
    print(f'[{current_time}] Bot restarted. Logged in as {client.user}')
    await slash.sync_all_commands()


@slash.slash(
    name="clear",
    description="Clear a specified number of messages in the current channel.",
    options=[
        create_option(
            name="amount",
            description="The number of messages to delete.",
            option_type=4,
            required=True,
        )
    ],
)
@commands.has_permissions(manage_messages=True)
async def clear(ctx: SlashContext, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    response = await ctx.send(f"{amount} messages deleted.")
    await asyncio.sleep(3)
    await response.delete()


@slash.slash(
    name="cerebralInitiation",
    description="Activate AI setup in the current channel.",
)
async def cerebral_initiation(ctx: SlashContext):
    global selected_channel
    selected_channel = ctx.channel
    await ctx.send(f"AI setup is now active in {selected_channel.mention}. Type any message, and the AI will respond as a normal user.")

@slash.slash(
    name="WhyisRobertonotonline",
    description="Generate a story about why Roberto is not online",
)
async def why_is_roberto_not_online(ctx: SlashContext):
    prompts = [
        "Generate a story about Roberto getting lost in a forest while hiking.",
        "Generate a story about Roberto's computer crashing and losing all of his data.",
        "Generate a story about Roberto getting kidnapped by aliens.",
        "Generate a story about Roberto's house being flooded due to a plumbing accident.",
        "Generate a story about Roberto accidentally eating some bad sushi and getting food poisoning.",
        "Generate a story about Roberto getting lost in a dream and unable to wake up.",
        "Generate a story about Roberto getting trapped in a video game.",
    ]
    # Select a random prompt from the list
    prompt = random.choice(prompts)

    # Generate a random seed
    seed = random.randint(0, 1000000)

    # Call the OpenAI API to generate a story based on the prompt and seed
    story = generate_text(prompt, seed=seed)

    # Send the generated story to the Discord channel
    await ctx.send(story)

@slash.slash(
    name="joinvc",
    description="Ask everyone to join the specified voice channel",
    options=[
        create_option(
            name="voice_channel_name",
            description="The name of the voice channel",
            option_type=3,
            required=True,
        ),
    ],
)
async def join_vc(ctx: SlashContext, voice_channel_name: str):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=voice_channel_name)
    if voice_channel:
        general_channel = discord.utils.get(ctx.guild.text_channels, name="general")
        if general_channel:
            await general_channel.send(f"@everyone Join the '{voice_channel_name}' voice channel immediately!")
        else:
            await ctx.send("The 'general' text channel was not found.")
    else:
        await ctx.send("Voice channel not found.")

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

    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    await client.process_commands(message)

    if message.channel == selected_channel:
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
        await message.channel.send(f"AI Response: {generated_text}")

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if after.channel.name == "THE OLIGARCHY":
            oligarchy_channel = discord.utils.get(member.guild.text_channels, name="oligarchy")
            ruler_role = discord.utils.get(member.guild.roles, name="Ruler")
            if oligarchy_channel and ruler_role:
                await oligarchy_channel.send(f"{member.mention} joined the 'THE OLIGARCHY' voice channel. {ruler_role.mention}")


client.run(token)

