import json
from datetime import datetime
from nebula_feed import config

# util function
def hex_to_int(hex) -> int:
    return int(hex, 16)

# class to collect info available in icx transaction
class TxInfo:
    def __init__(self, tx: json) -> None:
        self.txHash = str(tx["txHash"])
        self.contract = str(tx["to"])
        self.address = str(tx["from"])
        self.timestamp_iso = datetime.fromtimestamp(tx["timestamp"] / 1000000).replace(microsecond=0).isoformat()
        self.timestamp = int(tx["timestamp"] / 1000000)
        self.cost = f'{int(tx["value"]) / 10 ** 18 :.2f} ICX'
        self.method = tx["data"]["method"]

        # tokens claimed for credits are transffered from specifc address rather than claiming contract:
        if self.method == "transfer":
            self.contract = self.address
            self.address = str(tx["data"]["params"]["_to"])
            self.tokenId = hex_to_int(tx["data"]["params"]["_tokenId"])
            self.orderId = 0
        elif self.method == "createBuyOrder" or self.method == "createSellOrder":
            self.tokenId = hex_to_int(tx["data"]["params"]["_tokenId"])
            self.orderId = 0
        elif self.method == "buyTokens" or self.method == "sellTokens":
            self.tokenId = self.get_TokenIdFromOrderId()
            self.orderId = hex_to_int(tx["data"]["params"]["_orderId"])
        else:
            self.tokenId = hex_to_int(tx["data"]["params"]["_token_id"])
            self.orderId = 0

        if self.method == "create_auction":
            self.amount = ""
            self.set_price = ""
            self.starting_price = f'{hex_to_int(tx["data"]["params"]["_starting_price"]) / 10 ** 18 :.2f} ICX'
            self.duration_in_hours = str(hex_to_int(tx["data"]["params"]["_duration_in_hours"]))
        elif self.method == "list_token":
            self.amount = ""
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
            self.starting_price = ""
            self.duration_in_hours = ""
        elif self.method == "createSellOrder" or self.method == "createBuyOrder":
            self.amount = str(hex_to_int(tx["data"]["params"]["_amount"]))
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
            self.starting_price = ""
            self.duration_in_hours = ""
        elif self.method == "buyTokens" or self.method == "sellTokens":
            self.amount = str(hex_to_int(tx["data"]["params"]["_amount"]))
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
            self.starting_price = ""
            self.duration_in_hours = ""
        else:
            self.amount = ""
            self.set_price = ""
            self.starting_price = ""
            self.duration_in_hours = ""

    def get_ICXTransfer(self) -> str:
        txResult = config.icon_service.get_transaction_result(self.txHash)
        icx_amt = ""
        if txResult["status"] == 1: #success
            for x in txResult["eventLogs"]:
                if x["scoreAddress"] == config.NebulaPlanetTokenCx or x["scoreAddress"] == config.NebulaSpaceshipTokenCx:
                    if "ICXTransfer(Address,Address,int)" in x["indexed"]:
                        icx_amt = f'{hex_to_int(x["indexed"][3]) / 10 ** 18 :.2f} ICX'
                        break
        return icx_amt

    def get_TokenIdFromOrderId(self) -> int:
        txResult = config.icon_service.get_transaction_result(self.txHash)
        tokenId = 0
        if txResult["status"] == 1: #success
            for x in txResult["eventLogs"]:
                if x["scoreAddress"] == config.NebulaMultiTokenCx:
                    if "BuyTokens(int,int,Address,Address,int,int)" in x["indexed"] or "SellTokens(int,int,Address,Address,int,int)" in x["indexed"]:
                        if hex_to_int(x["indexed"][1]) == self.orderId:
                            tokenId = hex_to_int(x["indexed"][2])
                            break
        return tokenId
