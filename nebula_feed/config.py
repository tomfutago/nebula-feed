import os
from dotenv import load_dotenv
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# load env variables
is_heroku = os.getenv("IS_HEROKU", None)
if not is_heroku:
    load_dotenv()

# env vars
db_url = os.getenv("DATABASE_URL")
discord_log_webhook = os.getenv("DISCORD_LOG_WEBHOOK")

discord_claimed_webhook = os.getenv("DISCORD_CLAIMED_WEBHOOK")
discord_planets_webhook = os.getenv("DISCORD_PLANETS_WEBHOOK")
discord_ships_webhook = os.getenv("DISCORD_SHIPS_WEBHOOK")
discord_items_webhook = os.getenv("DISCORD_ITEMS_WEBHOOK")

discord_claimed_webhook_2 = os.getenv("DISCORD_CLAIMED_WEBHOOK_2")
discord_planets_webhook_2 = os.getenv("DISCORD_PLANETS_WEBHOOK_2")
discord_ships_webhook_2 = os.getenv("DISCORD_SHIPS_WEBHOOK_2")
discord_items_webhook_2 = os.getenv("DISCORD_ITEMS_WEBHOOK_2")

# custom emoji IDs - removed as discord complains about excedding API rate limits
#credits_emoji = os.getenv("credits_emoji")
#industry_emoji = os.getenv("industry_emoji")
#research_emoji = os.getenv("research_emoji")
# todo: add ship modifiers once available on official PN discord

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaSpaceshipTokenCx = "cx943cf4a4e4e281d82b15ae0564bbdcbf8114b3ec"
NebulaTokenClaimingCx = "cx4bfc45b11cf276bb58b3669076d99bc6b3e4e3b8"
NebulaNonCreditClaim = "hx888ed0ff5ebc119e586b5f3d4a0ef20eaa0ed123"
NebulaMultiTokenCx = "cx85954d0dae92b63bf5cba03a59ca4ffe687bad0a"
