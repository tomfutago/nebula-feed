import sys
import json
import requests
from time import sleep
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException
from discord_webhook import DiscordWebhook, DiscordEmbed

import icx_tx
import pn_token

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaSpaceshipTokenCx = "cx943cf4a4e4e281d82b15ae0564bbdcbf8114b3ec"
NebulaTokenClaimingCx = "cx4bfc45b11cf276bb58b3669076d99bc6b3e4e3b8"

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# function for making a call
def call(to, method, params):
    call = CallBuilder().to(to).method(method).params(params).build()
    result = icon_service.call(call)
    return result


# latest block height
block_height = icon_service.get_block("latest")["height"]

while True:
    try:
        block = icon_service.get_block(block_height)
        #print("block:", block_height)
    except JSONRPCException:
        sleep(2)
        continue
    else:
        try:
            for tx in block["confirmed_transaction_list"]:
                if "to" in tx:
                    if tx["to"] == NebulaPlanetTokenCx or tx["to"] == NebulaSpaceshipTokenCx or tx["to"] == NebulaTokenClaimingCx:
                        try:
                            # check if tx uses expected method - if not skip and move on
                            method = tx["data"]["method"]
                            #print("block:", block_height, "method:", method, "processing..")

                            expected_methods = [
                                "claim_token", "create_auction", "list_token", "place_bid", "purchase_token",
                                "finalize_auction", "return_unsold_item", "delist_token"
                            ]
                            if method not in expected_methods:
                                continue

                            # create instance of current transaction
                            txInfoCurrent = icx_tx.TxInfo(tx)

                            # check if tx was successful - if not skip and move on
                            txResult = icon_service.get_transaction_result(txInfoCurrent.txHash)
                            # status : 1 on success, 0 on failure
                            if txResult["status"] == 0:
                                continue

                            # to pull token info for NebulaTokenClaimingCx - NebulaPlanetTokenCx contract needs to be used
                            if txInfoCurrent.contract == NebulaTokenClaimingCx:
                                txInfoCurrent.contract = NebulaPlanetTokenCx
                            
                            # pull token details - if operation fails skip and move on
                            tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()

                            # check if json ok - if not skip and move on
                            if "error" in tokenInfo:
                                print("token info contains 'error'..")
                                continue

                            # get token info
                            if txInfoCurrent.contract == NebulaPlanetTokenCx:
                                token = pn_token.Planet(txInfoCurrent, tokenInfo)
                            elif txInfoCurrent.contract == NebulaSpaceshipTokenCx:
                                token = pn_token.Spaceship(txInfoCurrent, tokenInfo)

                            # check if "UNDISCOVERED PLANET" - if so, skip and move on
                            #if token.isUndiscovered:
                            #    print("undiscovered planet :(")
                            #    continue

                            if len(token.info) > 0:
                                webhook = DiscordWebhook(url=token.discord_webhook)
                                embed = DiscordEmbed(title=token.title, description=token.generate_discord_info(), color=token.set_color())
                                embed.set_thumbnail(url=token.image_url)
                                embed.set_footer(text=token.footer)
                                embed.set_timestamp(token.timestamp)
                                webhook.add_embed(embed)
                                response = webhook.execute()
                        except:
                            print("Error: {}. {}, line: {}".format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
                            continue

            block_height += 1
        except:
            sleep(2)
            continue
