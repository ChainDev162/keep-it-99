import discord
from discord.ext import commands
import json
import os

# Intents are required to receive certain events
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Set your bot's prefix and define intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Remove the default help command
bot.remove_command('help')

# JSON file to store monitored channels
CONFIG_FILE = 'channels.json'

# Load monitored channels from JSON file or initialize empty dict
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        channels_to_monitor = json.load(f)
else:
    channels_to_monitor = {}

def save_channels():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(channels_to_monitor, f, indent=4)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    # If you want to send a message to a specific channel
    channel = bot.get_channel()  # Replace with your channel ID
    if channel:
        await channel.send("🥱 I'm up")

@bot.event
async def on_message(message):
    if str(message.channel.id) in channels_to_monitor:
        # Fetch messages in the channel
        messages = [msg async for msg in message.channel.history(limit=100)]
        if len(messages) > 99:
            # Delete older messages if there are more than 99, change to your liking
            for msg in messages[99:]:
                await msg.delete()
    await bot.process_commands(message)

@bot.command(name='setup')
@commands.has_permissions(manage_channels=True)
async def setup(ctx, *channel_ids):
    global channels_to_monitor
    channels_to_monitor = {str(ch): f"Channel {ch}" for ch in channel_ids}
    save_channels()
    
    # Confirm the channels have been set up
    await ctx.send(f"Setup complete. Monitoring {len(channels_to_monitor)} channels.")

@bot.command(name='add-channel')
@commands.has_permissions(manage_channels=True)
async def add_channel(ctx, alias: str, channel_id: int):
    channel_id_str = str(channel_id)
    if channel_id_str not in channels_to_monitor:
        channels_to_monitor[channel_id_str] = alias
        save_channels()
        await ctx.send(f"Added channel '{alias}' with ID {channel_id} to the monitored list.")
    else:
        await ctx.send(f"Channel with ID {channel_id} is already being monitored as '{channels_to_monitor[channel_id_str]}'.")

@bot.command(name='add-channels')
@commands.has_permissions(manage_channels=True)
async def add_channels(ctx, *alias_channel_pairs):
    added_channels = []
    for alias, channel_id in zip(alias_channel_pairs[::2], alias_channel_pairs[1::2]):
        channel_id_str = str(channel_id)
        if channel_id_str not in channels_to_monitor:
            channels_to_monitor[channel_id_str] = alias
            added_channels.append(f"{alias} ({channel_id})")
    if added_channels:
        save_channels()
        await ctx.send(f"Added channels: {', '.join(added_channels)} to the monitored list.")
    else:
        await ctx.send("No new channels were added. They might already be monitored.")

@bot.command(name='remove-channel')
@commands.has_permissions(manage_channels=True)
async def remove_channel(ctx, alias: str):
    channel_to_remove = None
    for ch_id, ch_alias in channels_to_monitor.items():
        if ch_alias == alias:
            channel_to_remove = ch_id
            break
    
    if channel_to_remove:
        del channels_to_monitor[channel_to_remove]
        save_channels()
        await ctx.send(f"Removed channel '{alias}' from the monitored list.")
    else:
        await ctx.send(f"Channel with alias '{alias}' is not being monitored.")

@bot.command(name='remove-channels')
@commands.has_permissions(manage_channels=True)
async def remove_channels(ctx, *aliases):
    removed_channels = []
    for alias in aliases:
        channel_to_remove = None
        for ch_id, ch_alias in channels_to_monitor.items():
            if ch_alias == alias:
                channel_to_remove = ch_id
                break
        if channel_to_remove:
            del channels_to_monitor[channel_to_remove]
            removed_channels.append(alias)
    if removed_channels:
        save_channels()
        await ctx.send(f"Removed channels: {', '.join(removed_channels)} from the monitored list.")
    else:
        await ctx.send("No channels were removed. They might not have been monitored.")

@bot.command(name='list-channels')
@commands.has_permissions(manage_channels=True)
async def list_channels(ctx):
    if channels_to_monitor:
        channel_list = "\n".join([f"{alias}: {ch_id}" for ch_id, alias in channels_to_monitor.items()])
        await ctx.send(f"Monitored channels:\n{channel_list}")
    else:
        await ctx.send("No channels are currently being monitored.")

@bot.command(name='help')
async def custom_help_command(ctx):
    embed = discord.Embed(title="Bot Commands", description="List of available commands", color=0x00ff00)

    embed.add_field(name="`!setup <channel_ids...>`", value="Setup monitoring for multiple channels by ID.", inline=False)
    embed.add_field(name="`!add-channel <alias> <channel_id>`", value="Add a single channel to monitor with an alias.", inline=False)
    embed.add_field(name="`!add-channels <alias1> <channel_id1> <alias2> <channel_id2> ...`", value="Add multiple channels to monitor with aliases.", inline=False)
    embed.add_field(name="`!remove-channel <alias>`", value="Remove a single channel from monitoring by alias.", inline=False)
    embed.add_field(name="`!remove-channels <alias1> <alias2> ...", value="Remove multiple channels from monitoring by alias.", inline=False)
    embed.add_field(name="`!list-channels`", value="List all currently monitored channels with aliases and IDs.", inline=False)
    embed.add_field(name="`!help`", value="Display this help message.", inline=False)

    embed.set_footer(text="Customize this help message as needed!")

    await ctx.send(embed=embed)

# Replace with your bot's token
bot.run('')
