import os
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed

# load discord webhook
load_dotenv()
discord_webhook = os.getenv("TEST_CLAIMED_DISCORD_WEBHOOK")

webhook = DiscordWebhook(url=discord_webhook)

embed = DiscordEmbed(title="test")
#embed.add_embed_field(name="field", value=":Credit:")
embed.set_description("<:Credit:884088541813039185>")

webhook.add_embed(embed)
response = webhook.execute()
