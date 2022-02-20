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
        self.orderId = 0
        self.tokenId = 0
        self.amount = ""
        self.set_price = ""
        self.starting_price = ""
        self.duration_in_hours = ""
        tmpTokenId = "0"

        # method specific properties
        if self.method == "buyTokens" or self.method == "sellTokens" or self.method == "cancelOrder":
            self.orderId = hex_to_int(tx["data"]["params"]["_orderId"])

        if self.method == "transfer":
            self.contract = self.address # tokens claimed for credits are transffered from specifc address rather than claiming contract
            self.address = str(tx["data"]["params"]["_to"])
            tmpTokenId = tx["data"]["params"]["_tokenId"]
        elif self.method == "createBuyOrder" or self.method == "createSellOrder":
            tmpTokenId = tx["data"]["params"]["_tokenId"]
        elif self.method == "buyTokens" or self.method == "sellTokens":
            tmpTokenId = self.get_TokenIdFromOrderId()
        elif self.method == "cancelOrder":
            tmpTokenId = "0"
        else:
            tmpTokenId = tx["data"]["params"]["_token_id"]
        
        # convert TokenId to int
        if tmpTokenId[:2] == "0x":
            self.tokenId = hex_to_int(tmpTokenId)
        else:
            self.tokenId = int(tmpTokenId)

        if self.method == "create_auction":
            self.starting_price = f'{hex_to_int(tx["data"]["params"]["_starting_price"]) / 10 ** 18 :.2f} ICX'
            self.duration_in_hours = str(hex_to_int(tx["data"]["params"]["_duration_in_hours"]))
        elif self.method == "list_token":
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
        elif self.method == "createBuyOrder" or self.method == "createSellOrder":
            self.amount = str(hex_to_int(tx["data"]["params"]["_amount"]))
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
        elif self.method == "buyTokens" or self.method == "sellTokens":
            self.amount = str(hex_to_int(tx["data"]["params"]["_amount"]))

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

    def get_TokenIdFromOrderId(self) -> str:
        txResult = config.icon_service.get_transaction_result(self.txHash)
        tokenId = ""
        if txResult["status"] == 1: #success
            for x in txResult["eventLogs"]:
                if x["scoreAddress"] == config.NebulaMultiTokenCx:
                    if "BuyTokens(int,int,Address,Address,int,int)" in x["indexed"] or "SellTokens(int,int,Address,Address,int,int)" in x["indexed"]:
                        if hex_to_int(x["indexed"][1]) == self.orderId:
                            tokenId = x["indexed"][2]
                            break
        return tokenId
