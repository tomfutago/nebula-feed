import os
from discord.ext import commands
from dotenv import load_dotenv

from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
discord_guild = os.getenv('DISCORD_GUILD')

icon_service = IconService(HTTPProvider('https://ctz.solidwallet.io', 3))


bot = commands.Bot(command_prefix='!')

@bot.command(name='balance', help='')
async def balance(ctx):
    response = icon_service.get_balance('hxdaf3b8bf5844ed3ebf104f2e8f13b4f5ceff2160')
    await ctx.send(response / 10 ** 18)

bot.run(discord_token)
