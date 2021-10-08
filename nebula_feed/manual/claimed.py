import sys
import json
import requests
from time import sleep
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from discord_webhook import DiscordWebhook, DiscordEmbed

from nebula_feed import icx_tx
from nebula_feed import pn_token

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaTokenClaimingCx = "cx4bfc45b11cf276bb58b3669076d99bc6b3e4e3b8"
NebulaNonCreditClaim = "hx888ed0ff5ebc119e586b5f3d4a0ef20eaa0ed123"

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# function for making a call
def call(to, method, params):
    call = CallBuilder().to(to).method(method).params(params).build()
    result = icon_service.call(call)
    return result

def AddClaimPlanet(block_height):
    try:
        block = icon_service.get_block(block_height)

        for tx in block["confirmed_transaction_list"]:
            if "to" in tx:
                if tx["to"] == NebulaTokenClaimingCx or tx["from"] == NebulaNonCreditClaim:
                    # check if tx uses expected method - if not skip and move on
                    method = tx["data"]["method"]
                    
                    if tx["to"] == NebulaTokenClaimingCx and method != "claim_token":
                        continue
                    elif tx["from"] == NebulaNonCreditClaim and method != "transfer":
                        continue

                    # create instance of current transaction
                    txInfoCurrent = icx_tx.TxInfo(tx)

                    # check if tx was successful - if not skip and move on
                    txResult = icon_service.get_transaction_result(txInfoCurrent.txHash)
                    # status : 1 on success, 0 on failure
                    if txResult["status"] == 0:
                        continue

                    # to pull token info for NebulaTokenClaimingCx - NebulaPlanetTokenCx contract needs to be used
                    txInfoCurrent.contract = NebulaPlanetTokenCx
                    
                    # pull token details - if operation fails skip and move on
                    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()

                    # check if json ok - if not skip and move on
                    if "error" in tokenInfo:
                        print("token info contains 'error'..")
                        continue

                    # get token info
                    token = pn_token.Planet(txInfoCurrent, tokenInfo)

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

###################################
AddClaimPlanet(block_height=40393974)
AddClaimPlanet(block_height=40405184)
AddClaimPlanet(block_height=40425171)
AddClaimPlanet(block_height=40427632)
AddClaimPlanet(block_height=40429355)
sleep(15)
AddClaimPlanet(block_height=40448016)
AddClaimPlanet(block_height=40452793)
AddClaimPlanet(block_height=40459988)
AddClaimPlanet(block_height=40466170)
AddClaimPlanet(block_height=40475546)
sleep(15)
AddClaimPlanet(block_height=40493554)
AddClaimPlanet(block_height=40514571) #credits
AddClaimPlanet(block_height=40525655) #credits
AddClaimPlanet(block_height=40527763) #credits
AddClaimPlanet(block_height=40533645)
sleep(15)
AddClaimPlanet(block_height=40535420)
AddClaimPlanet(block_height=40548432)
AddClaimPlanet(block_height=40549836)
AddClaimPlanet(block_height=40550081)
sleep(15)
AddClaimPlanet(block_height=40550141)
AddClaimPlanet(block_height=40552537)
AddClaimPlanet(block_height=40564038) #credits
AddClaimPlanet(block_height=40568917)
sleep(15)
AddClaimPlanet(block_height=40569476)
AddClaimPlanet(block_height=40570041) #credits
AddClaimPlanet(block_height=40571164)
AddClaimPlanet(block_height=40571443)
AddClaimPlanet(block_height=40573677) #credits
sleep(15)
AddClaimPlanet(block_height=40575468)
AddClaimPlanet(block_height=40577998)
AddClaimPlanet(block_height=40578623)
AddClaimPlanet(block_height=40582084)
AddClaimPlanet(block_height=40590873)
AddClaimPlanet(block_height=40592998)
AddClaimPlanet(block_height=40598139) #credits
sleep(15)
AddClaimPlanet(block_height=40606754)
AddClaimPlanet(block_height=40613779)
AddClaimPlanet(block_height=40616690)
AddClaimPlanet(block_height=40625571) #credits
AddClaimPlanet(block_height=40641980)
AddClaimPlanet(block_height=40647545)
