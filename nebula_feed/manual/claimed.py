import sys
import psycopg2
import requests
from datetime import datetime
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from discord_webhook import DiscordWebhook, DiscordEmbed

from nebula_feed import config
from nebula_feed import icx_tx
from nebula_feed import pn_token

conn = psycopg2.connect(config.db_url, sslmode="require")
cur = conn.cursor()

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
        #print(json.dumps(block, indent = 4))

        for tx in block["confirmed_transaction_list"]:
            if "to" in tx:
                if tx["to"] == config.NebulaPlanetTokenCx or tx["to"] == config.NebulaTokenClaimingCx:
                    # check if tx uses expected method - if not skip and move on
                    method = tx["data"]["method"]
                    
                    if tx["to"] == config.NebulaTokenClaimingCx and method != "claim_token":
                        continue
                    elif tx["from"] == config.NebulaNonCreditClaim and method != "transfer":
                        continue

                    # create instance of current transaction
                    txInfoCurrent = icx_tx.TxInfo(tx)

                    # check if tx was successful - if not skip and move on
                    txResult = icon_service.get_transaction_result(txInfoCurrent.txHash)
                    # status : 1 on success, 0 on failure
                    if txResult["status"] == 0:
                        continue

                    # to pull token info for NebulaTokenClaimingCx - NebulaPlanetTokenCx contract needs to be used
                    if txInfoCurrent.contract == config.NebulaTokenClaimingCx or txInfoCurrent.contract == config.NebulaNonCreditClaim:
                        txInfoCurrent.contract = config.NebulaPlanetTokenCx
                    
                    # pull token details - if operation fails skip and move on
                    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()

                    # check if json ok - if not skip and move on
                    if "error" in tokenInfo:
                        print("token info contains 'error'..")
                        continue

                    # get token info
                    token = pn_token.Planet(txInfoCurrent, tokenInfo)

                    cur.execute("insert into ClaimedPlanets(TokenId, PlanetName, ClaimedDate) values (%s, %s, %s);",
                        (txInfoCurrent.tokenId, token.name, txInfoCurrent.timestamp_iso))

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
AddClaimPlanet(block_height=40731951)

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()
