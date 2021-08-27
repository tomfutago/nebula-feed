import os
import json
import requests
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException
from discord_webhook import DiscordWebhook, DiscordEmbed

# load discord webhook
is_heroku = os.getenv('IS_HEROKU', None)

if not is_heroku:
    load_dotenv()

discord_webhook = os.getenv("DISCORD_WEBHOOK")

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaTokenClaimingCx = "cx4bfc45b11cf276bb58b3669076d99bc6b3e4e3b8"

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# function for making a call
def call(to, method, params):
    call = CallBuilder()\
        .to(to)\
        .method(method)\
        .params(params)\
        .build()
    result = icon_service.call(call)
    return result

def set_color(rarity: str) -> str:
    rarity = rarity.lower()
    if rarity == "common":
        color = "808B96"
    elif rarity == "uncommon":
        color = "FDFEFE"
    elif rarity == "rare":
        color = "3498DB"
    elif rarity == "legendary":
        color = "8E44AD"
    elif rarity == "mythic":
        color = "F39C12"
    return color


# latest block height
block_height = icon_service.get_block("latest")["height"]

while True:
    try:
        block = icon_service.get_block(block_height)
        block -= 30 # keep it 30 blocks (60 seconds) behind in hope to avoid "UNDISCOVERED PLANET" (minting time?) issue 
        print("block:", block_height)
    except JSONRPCException:
        sleep(2)
        continue
    else:
        try:
            move_on = True
            for tx in block["confirmed_transaction_list"]:
                if "to" in tx:
                    if tx["to"] == NebulaTokenClaimingCx and tx["data"]["method"] == "claim_token":
                        # pull token details - max tries 5x
                        # if name == "UNDISCOVERED PLANET" - wait 5s and try again
                        # 60 seconds delay on the main loop should allow for just 1 pass through this loop
                        # but keeping in the additional retry loop as a safety net
                        for n in range(5):
                            txHash = tx["txHash"]
                            txDetail = icon_service.get_transaction(txHash)
                            tokenId = int(txDetail["data"]["params"]["_token_id"], 16)

                            try:
                                planetInfo = requests.get(call(NebulaPlanetTokenCx, "tokenURI", {"_tokenId": tokenId})).json()
                            except JSONRPCException:
                                sleep(5)
                                move_on = False
                                continue

                            # if json is ok - check name
                            if "error" not in planetInfo:
                                name = str(planetInfo["name"]).upper()
                                if name == "UNDISCOVERED PLANET":
                                    sleep(5)
                                    move_on = False
                                else:
                                    move_on = True
                                    break
                        
                        # retrieving planet details failed - move on
                        if move_on == False:
                            break

                        # get basic info about the token
                        owner = txDetail["from"]
                        #timestamp = datetime.fromtimestamp(txDetail["timestamp"] / 1000000).replace(microsecond=0).isoformat()
                        timestamp = int(txDetail["timestamp"] / 1000000)
                        cost = txDetail["value"] / 10 ** 18

                        # obfuscate owner's address
                        owner = owner[:8] + ".." + owner[34:]
                        rarity = str(planetInfo["rarity"]).lower()
                        generation = str(planetInfo["generation"]).upper()
                        subtitle = (rarity + " / " + generation).upper()
                        type = str(planetInfo["type"]).lower()
                        credits = str(planetInfo["credits"])
                        industry = str(planetInfo["industry"])
                        research = str(planetInfo["research"])
                        income = credits + "C / " + industry + "I / " + research + "R"
                        image_url = planetInfo["image"]
                        external_link = planetInfo["external_link"]
                        
                        special_resources = []
                        for special in planetInfo["specials"]:
                            special_resources.append(str(special["name"]))
                        specials = ', '.join(special_resources)

                        # Markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
                        info = "\nType: " + type + "\nIncome: " + income
                        
                        if len(specials) > 0:
                            info += "\nSpecials: " + specials
                        
                        info += "\nHappy owner: " + owner + "\n[Check it out here](" + external_link + ")"
                        
                        color = set_color(rarity)

                        if len(info) > 0:
                            webhook = DiscordWebhook(url=discord_webhook)

                            embed = DiscordEmbed(title=name, color=color)
                            embed.set_thumbnail(url=image_url)
                            embed.add_embed_field(name=subtitle, value=info)
                            embed.set_footer(text="Claimed on ")
                            embed.set_timestamp(timestamp)
                            
                            webhook.add_embed(embed)
                            response = webhook.execute()

            if move_on:
                block_height += 1
        except:
            sleep(2)
            continue
