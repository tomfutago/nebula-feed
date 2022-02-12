import sys
import requests
import psycopg2
from time import sleep
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException
from discord_webhook import DiscordWebhook, DiscordEmbed
from nebula_feed import config, icx_tx, pn_token, pn_items

# function for making a call
def call(to, method, params):
    call = CallBuilder().to(to).method(method).params(params).build()
    result = config.icon_service.call(call)
    return result

# function for adding new record to ClaimedPlanets table
def add_to_ClaimedPlanets(TokenId: int, PlanetName: str, ClaimedDate: str):
    # open db connection and cursor to perform db operations
    conn = psycopg2.connect(config.db_url, sslmode="require")
    cur = conn.cursor()

    # add new record
    cur.execute(
        "insert into ClaimedPlanets(TokenId, PlanetName, ClaimedDate) values (%s, %s, %s);",
        (TokenId, PlanetName, ClaimedDate)
    )

    # commit and close connection
    conn.commit()
    cur.close()
    conn.close()

# function for sending error msg to discord webhook
def send_log_to_webhook(block_height: int, txHash: str, method: str, error: str):
    err_msg = "Project Nebula log"
    err_msg += "\nblock_height: " + str(block_height)
    err_msg += "\ntxHash: " + txHash
    err_msg += "\nmethod: " + method
    err_msg += "\nERROR: " + error
    err_msg += "\n"
    webhook = DiscordWebhook(url=config.discord_log_webhook, rate_limit_retry=True, content=err_msg)
    response = webhook.execute()
    return response


# latest block height
block_height = config.icon_service.get_block("latest")["height"]

while True:
    try:
        block = config.icon_service.get_block(block_height)
        #print("block:", block_height)
    except JSONRPCException:
        sleep(2)
        continue
    else:
        try:
            for tx in block["confirmed_transaction_list"]:
                if "to" in tx:
                    if tx["to"] == config.NebulaPlanetTokenCx or tx["to"] == config.NebulaSpaceshipTokenCx \
                       or tx["to"] == config.NebulaTokenClaimingCx or tx["to"] == config.NebulaMultiTokenCx:
                        try:
                            # check if tx uses expected method - if not skip and move on
                            method = tx["data"]["method"]
                            #print("block:", block_height, "method:", method, "processing..")

                            if tx["from"] == config.NebulaNonCreditClaim:
                                if method != "transfer":
                                    err_msg = "NebulaNonCreditClaim with non-transfer method.."
                                    response = send_log_to_webhook(block_height, tx["txHash"], method, err_msg)
                                    continue
                            else:
                                expected_methods = [
                                    "claim_token", "create_auction", "list_token", "place_bid", "purchase_token",
                                    "finalize_auction", "return_unsold_item", "delist_token",
                                    "createSellOrder", "createBuyOrder", "buyTokens", "cancelOrder"
                                ]
                                if method not in expected_methods:
                                    continue
                            
                            # add delay to avoid error msg below after ICON 2.0 upgrade
                            # iconsdk.exception.JSONRPCException: {'code': -31003, 'message': 'Executing : Executing'}
                            sleep(2)

                            # check if tx was successful - if not skip and move on
                            txResult = config.icon_service.get_transaction_result(tx["txHash"])
                            # status : 1 on success, 0 on failure
                            if txResult["status"] == 0:
                                continue

                            # create instance of current transaction
                            txInfoCurrent = icx_tx.TxInfo(tx)

                            # to pull token info for NebulaTokenClaimingCx - NebulaPlanetTokenCx contract needs to be used
                            if txInfoCurrent.contract == config.NebulaTokenClaimingCx or txInfoCurrent.contract == config.NebulaNonCreditClaim:
                                txInfoCurrent.contract = config.NebulaPlanetTokenCx
                                sleep(60)
                            
                            # pull token details
                            if txInfoCurrent.contract == config.NebulaSpaceshipTokenCx or txInfoCurrent.contract == config.NebulaPlanetTokenCx:
                                tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
                            elif txInfoCurrent.contract == config.NebulaMultiTokenCx:
                                tokenInfo = call(txInfoCurrent.contract, "getOrder", {"_orderId": txInfoCurrent.orderId})

                            # check if json ok - if not skip and move on
                            if "error" in tokenInfo:
                                # send to log webhook
                                response = send_log_to_webhook(block_height, tx["txHash"], method, "token info contains 'error'")
                                continue

                            # get token info
                            if txInfoCurrent.contract == config.NebulaPlanetTokenCx:
                                token = pn_token.Planet(txInfoCurrent, tokenInfo)
                            elif txInfoCurrent.contract == config.NebulaSpaceshipTokenCx:
                                token = pn_token.Spaceship(txInfoCurrent, tokenInfo)
                            elif txInfoCurrent.contract == config.NebulaMultiTokenCx:
                                token = pn_items.PNItem(txInfoCurrent, tokenInfo)

                            if len(token.info) > 0 and len(token.name) > 0:
                                if token.isClaimed:
                                    add_to_ClaimedPlanets(txInfoCurrent.tokenId, token.name, txInfoCurrent.timestamp_iso)
                                
                                webhook = DiscordWebhook(url=token.discord_webhook, rate_limit_retry=True)
                                embed = DiscordEmbed(title=token.title, description=token.generate_discord_info(), color=token.set_color())
                                embed.set_thumbnail(url=token.image_url)
                                embed.set_footer(text=token.footer)
                                embed.set_timestamp(token.timestamp)
                                webhook.add_embed(embed)
                                response = webhook.execute()
                        except:
                            #send to log webhook
                            err_msg = "{}. {}, line: {}".format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)
                            response = send_log_to_webhook(block_height, tx["txHash"], method, err_msg)
                            continue

            block_height += 1
        except:
            sleep(2)
            continue
