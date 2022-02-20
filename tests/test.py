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

#block_height = 46400911 #buyTokens
block_height = 46402597 #sellTokens
#block_height = 46175845 #cancelOrder
#block_height = 46161894 #claim_token
#block_height = 46139022 #create_auction
#block_height = 46156240 #list_token
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
    tokenInfo = call(txInfoCurrent.contract, "getOrder", {"_orderId": txInfoCurrent.orderId})
    print(int(tokenInfo["_tokenId"], 16))
    token = pn_items.PNItem(txInfoCurrent, tokenInfo)
    #print(token.name)
    #print(int(tokenInfo["_amount"], 16))
    #print(f'{int(tokenInfo["_price"], 16) / 10 ** 18 :.2f} ICX')
    print(token.generate_discord_info())

if txInfoCurrent.contract == config.NebulaTokenClaimingCx or txInfoCurrent.contract == config.NebulaNonCreditClaim:
    txInfoCurrent.contract = config.NebulaPlanetTokenCx
    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
    #print(json.dumps(tokenInfo, indent=2))
    token = pn_token.Planet(txInfoCurrent, tokenInfo)
    print(token.generate_discord_info())

if txInfoCurrent.contract == config.NebulaSpaceshipTokenCx or txInfoCurrent.contract == config.NebulaPlanetTokenCx:
    tokenInfo = requests.get(call(txInfoCurrent.contract, "tokenURI", {"_tokenId": txInfoCurrent.tokenId})).json()
    #print(json.dumps(tokenInfo, indent=2))
    if txInfoCurrent.contract == config.NebulaPlanetTokenCx:
        token = pn_token.Planet(txInfoCurrent, tokenInfo)
    elif txInfoCurrent.contract == config.NebulaSpaceshipTokenCx:
        token = pn_token.Spaceship(txInfoCurrent, tokenInfo)
    print(token.generate_discord_info())
