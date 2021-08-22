import sys
import json
import requests
from datetime import datetime
from time import sleep
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException
from discord_webhook import DiscordWebhook, DiscordEmbed

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaTokenClaimingCx = "cx4bfc45b11cf276bb58b3669076d99bc6b3e4e3b8"

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# discord webhook
webhook = "https://discord.com/api/webhooks/879087983653961768/3vQxYZrecnjoa1xsfj_kVJ7-ozz63r_yNp3pi7jtJVOkS6cOKAAv7iS5s4gbolnnLMbF"

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

#block = icon_service.get_block(38641879)
#print(json.dumps(block, indent=4))

# latest block height
block_height = icon_service.get_block("latest")["height"]

while True:
    while True:
        try:
            block = icon_service.get_block(block_height)
        except JSONRPCException:
            sleep(2)
            continue
        else:
            for tx in block["confirmed_transaction_list"]:
                if "to" in tx:
                    if tx["to"] == NebulaTokenClaimingCx:
                        txHash = tx["txHash"]
                        txDetail = icon_service.get_transaction(txHash)
                        owner = txDetail["from"]
                        timestamp = datetime.fromtimestamp(txDetail["timestamp"] / 1000000).replace(microsecond=0).isoformat()
                        cost = txDetail["value"] / 10 ** 18
                        tokenId = int(txDetail["data"]["params"]["_token_id"], 16)

                        # pull json response through API
                        response_content = requests.get(call(NebulaPlanetTokenCx, "tokenURI", {"_tokenId": tokenId})).text

                        if is_json(response_content):
                            json_content = json.loads(response_content)
                        else:
                            continue

                        # if json is ok - get granual data
                        if "error" not in json_content:
                            # obfuscate owner's address
                            owner = owner[:10] + ".." + owner[34:]
                            
                            # get basic info about the token
                            token_type = str(json_content["token_type"]).lower()
                            generation = str(json_content["generation"]).upper()
                            rarity = str(json_content["rarity"]).lower()
                            name = str(json_content["name"]).title()
                            type = str(json_content["type"]).lower()
                            
                            special_resources = []
                            for special in json_content["specials"]:
                                special_resources.append(str(special["name"]))
                            specials = ', '.join(special_resources)

                        message = "\nowner: " + owner \
                                + "\nname: " + name \
                                + "\ngeneration: " + generation \
                                + "\nrarity: " + rarity \
                                + "\ntype: " + type \
                                + "\ntimestamp: " + str(timestamp).replace("T", " ") \
                                + "\ncost: " + str(cost) \
                                + "\nspecial resources: " + specials

                        webhook = DiscordWebhook(url=webhook, content=message)
                        response = webhook.execute()

        finally:
            block_height += 1
