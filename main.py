import discord
from discord.ext import commands
from discord import app_commands
import os


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

async def load_commands():
    for file in os.listdir('commands/'):
        if file.endswith('.py'):
            await client.load_extension(f'commands.{file[:-3]}')

@client.event
async def on_ready():
    await load_commands()
    await client.tree.sync()
    print('Conectado no discord !')

client.run(os.getenv('TOKEN'))