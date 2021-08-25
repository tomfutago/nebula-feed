import os
import sys
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
    try:
        call = CallBuilder()\
            .to(to)\
            .method(method)\
            .params(params)\
            .build()
        result = icon_service.call(call)
        return result
    except:
        __, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        e = "error: " + str(exception_object) + " at line number: " + str(line_number)
        return e

# check if valid json
def is_json(content: str):
    try:
        json_object = json.loads(content)
    except ValueError as e:
        return False
    return True

# latest block height
block_height = 38771900 # 38686216 #icon_service.get_block("latest")["height"]

while True:
    while True:
        try:
            block = icon_service.get_block(block_height)
        except JSONRPCException:
            sleep(2)
            continue
        else:
            try:
                move_on = True
                for tx in block["confirmed_transaction_list"]:
                    if "to" in tx:
                        if tx["to"] == NebulaTokenClaimingCx and tx["data"]["method"] == "claim_token":
                            message = ""
                            txHash = tx["txHash"]
                            txDetail = icon_service.get_transaction(txHash)
                            owner = txDetail["from"]
                            #timestamp = datetime.fromtimestamp(txDetail["timestamp"] / 1000000).replace(microsecond=0).isoformat()
                            timestamp = int(txDetail["timestamp"] / 1000000)
                            cost = txDetail["value"] / 10 ** 18
                            tokenId = int(txDetail["data"]["params"]["_token_id"], 16)

                            # pull token details
                            response_content = requests.get(call(NebulaPlanetTokenCx, "tokenURI", {"_tokenId": tokenId})).text

                            if is_json(response_content):
                                json_content = json.loads(response_content)
                            else:
                                continue

                            # if json is ok - get granual data
                            if "error" not in json_content:
                                # obfuscate owner's address
                                owner = owner[:8] + ".." + owner[34:]
                                
                                # get basic info about the token
                                name = str(json_content["name"]).upper()
                                if name == "UNDISCOVERED PLANET":
                                    sleep(5)
                                    move_on = False
                                    continue

                                rarity = str(json_content["rarity"]).lower()
                                generation = str(json_content["generation"]).upper()
                                subtitle = (rarity + " / " + generation).upper()
                                type = str(json_content["type"]).lower()
                                credits = str(json_content["credits"])
                                industry = str(json_content["industry"])
                                research = str(json_content["research"])
                                income = credits + "C / " + industry + "I / " + research + "R"
                                image_url = json_content["image"]
                                external_link = json_content["external_link"]
                                
                                special_resources = []
                                for special in json_content["specials"]:
                                    special_resources.append(str(special["name"]))
                                specials = ', '.join(special_resources)

                                # Markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
                                info = "\nType: " + type \
                                    + "\nIncome: " + income
                                
                                if len(specials) > 0:
                                    info += "\nSpecials: " + specials
                                
                                info += "\nHappy owner: " + owner \
                                    + "\n[Check it out here](" + external_link + ")"
                                
                                if rarity == "common":
                                    color = "2C3E50"
                                elif rarity == "uncommon":
                                    color = "FDFEFE"
                                elif rarity == "rare":
                                    color = "3498DB"
                                elif rarity == "legendary":
                                    color = "8E44AD"
                                elif rarity == "mythic":
                                    color = "F39C12"

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
