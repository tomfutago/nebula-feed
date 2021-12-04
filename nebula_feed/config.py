import os
from dotenv import load_dotenv

# load env variables
is_heroku = os.getenv("IS_HEROKU", None)
if not is_heroku:
    load_dotenv()

discord_log_webhook = os.getenv("DISCORD_LOG_WEBHOOK")
discord_claimed_webhook = os.getenv("DISCORD_CLAIMED_WEBHOOK")
discord_market_webhook = os.getenv("DISCORD_MARKET_WEBHOOK")
db_url = os.getenv("DATABASE_URL")

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
