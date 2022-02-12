"""
cost = "{:.2f}".format(int("146253000000000000000") / 10 ** 18) + " ICX"
cost = f"{int('146253000000000000000') / 10 ** 18 :.2f} ICX"
print(cost)
"""

from nebula_feed import config, icx_tx, pn_token, pn_items
from iconsdk.builder.call_builder import CallBuilder

def call(to, method, params):
    call = CallBuilder().to(to).method(method).params(params).build()
    result = config.icon_service.call(call)
    return result

block_height = 46085337
block = config.icon_service.get_block(block_height)

for tx in block["confirmed_transaction_list"]:
    if "to" in tx:
        if tx["to"] == config.NebulaMultiTokenCx:
            txInfoCurrent = icx_tx.TxInfo(tx)
            break

print(txInfoCurrent.method)
print(txInfoCurrent.orderId)
print(txInfoCurrent.tokenId)

tokenInfo = call(txInfoCurrent.contract, "getOrder", {"_orderId": txInfoCurrent.orderId})
print(int(tokenInfo["_tokenId"], 16))

if txInfoCurrent.contract == config.NebulaMultiTokenCx:
    token = pn_items.PNItem(txInfoCurrent, tokenInfo)

print(token.name)
print(int(tokenInfo["_amount"], 16))
print(f'{int(tokenInfo["_price"], 16) / 10 ** 18 :.2f} ICX')
