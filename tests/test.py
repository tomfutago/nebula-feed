"""
cost = "{:.2f}".format(int("146253000000000000000") / 10 ** 18) + " ICX"
cost = f"{int('146253000000000000000') / 10 ** 18 :.2f} ICX"
print(cost)
"""

import json
import requests
from nebula_feed import config, icx_tx, pn_token, pn_items
from iconsdk.builder.call_builder import CallBuilder

def call(to, method, params):
    call = CallBuilder().to(to).method(method).params(params).build()
    result = config.icon_service.call(call)
    return result

#block_height = 46538713 #46400911 #buyTokens
#block_height = 46402597 #sellTokens
#block_height = 46175845 #cancelOrder
#block_height = 46161894 #claim_token
#block_height = 46139022 #create_auction
#block_height = 46156240 #list_token
block_height = 46533984 #createSellOrder
block = config.icon_service.get_block(block_height)

for tx in block["confirmed_transaction_list"]:
    if "to" in tx:
        if tx["to"] == config.NebulaPlanetTokenCx or tx["to"] == config.NebulaSpaceshipTokenCx \
           or tx["to"] == config.NebulaTokenClaimingCx or tx["to"] == config.NebulaMultiTokenCx:
            txInfoCurrent = icx_tx.TxInfo(tx)
            break

print("method: ", txInfoCurrent.method)
print("orderId: ", txInfoCurrent.orderId)
print("tokenId: ", txInfoCurrent.tokenId)

if txInfoCurrent.contract == config.NebulaMultiTokenCx:
    orderInfo = call(txInfoCurrent.contract, "getOrder", {"_orderId": txInfoCurrent.orderId})
    if txInfoCurrent.tokenId == 0:
        txInfoCurrent.tokenId = int(orderInfo["_tokenId"], 16)
    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
    #print(json.dumps(tokenInfo, indent=2))
    #print(orderInfo)
    #print("tokenId (from order): ", int(orderInfo["_tokenId"], 16))
    token = pn_items.PNItem(txInfoCurrent, tokenInfo, orderInfo)
    #print(token.name)
    #print(int(tokenInfo["_amount"], 16))
    #print(f'{int(tokenInfo["_price"], 16) / 10 ** 18 :.2f} ICX')

if txInfoCurrent.contract == config.NebulaTokenClaimingCx or txInfoCurrent.contract == config.NebulaNonCreditClaim:
    txInfoCurrent.contract = config.NebulaPlanetTokenCx
    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
    #print(json.dumps(tokenInfo, indent=2))
    token = pn_token.Planet(txInfoCurrent, tokenInfo)

if txInfoCurrent.contract == config.NebulaSpaceshipTokenCx or txInfoCurrent.contract == config.NebulaPlanetTokenCx:
    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
    #print(json.dumps(tokenInfo, indent=2))
    if txInfoCurrent.contract == config.NebulaPlanetTokenCx:
        token = pn_token.Planet(txInfoCurrent, tokenInfo)
    elif txInfoCurrent.contract == config.NebulaSpaceshipTokenCx:
        token = pn_token.Spaceship(txInfoCurrent, tokenInfo)

print(token.title)
print(token.generate_discord_info())
print(token.image_url)
