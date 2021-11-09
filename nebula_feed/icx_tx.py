import json
from datetime import datetime
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException

# Project Nebula contract
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"

# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

# util function
def hex_to_int(hex) -> int:
    return int(hex, 16)

# not used atm..
class IcxBlock:
    def __init__(self) -> None:
        self.block_height = icon_service.get_block("latest")["height"]
        self.block = icon_service.get_block(self.block_height)

    def get_latest_block(self) -> dict:
        return icon_service.get_block("latest")

    def get_block(self, block: int) -> dict:
        return icon_service.get_block(block)
        
    def get_tx_result(self, tx_hash: str) -> dict:
        return icon_service.get_transaction_result(tx_hash)

    def call(self, to, method, params=None):
        try:
            call = CallBuilder().to(to).method(method).params(params).build()
            result = icon_service.call(call)
            return result
        except JSONRPCException as e:
            raise Exception(e)

# class to collect info available in icx transaction
class TxInfo:
    def __init__(self, tx: json) -> None:
        self.txHash = str(tx["txHash"])
        self.contract = str(tx["to"])
        self.address = str(tx["from"])
        #self.timestamp = datetime.fromtimestamp(tx["timestamp"] / 1000000).replace(microsecond=0).isoformat()
        self.timestamp = int(tx["timestamp"] / 1000000)
        self.cost = f'{int(tx["value"]) / 10 ** 18 :.2f} ICX'
        self.method = tx["data"]["method"]

        # tokens claimed for credits are transffered from specifc address rather than claiming contract:
        if self.method == "transfer":
            self.contract = self.address
            self.address = str(tx["data"]["params"]["_to"])
            self.tokenId = hex_to_int(tx["data"]["params"]["_tokenId"])
        else:
            self.tokenId = hex_to_int(tx["data"]["params"]["_token_id"])

        if self.method == "create_auction":
            self.set_price = ""
            self.starting_price = f'{hex_to_int(tx["data"]["params"]["_starting_price"]) / 10 ** 18 :.2f} ICX'
            self.duration_in_hours = str(hex_to_int(tx["data"]["params"]["_duration_in_hours"]))
        elif self.method == "list_token":
            self.set_price = f'{hex_to_int(tx["data"]["params"]["_price"]) / 10 ** 18 :.2f} ICX'
            self.starting_price = ""
            self.duration_in_hours = ""
        else:
            self.set_price = ""
            self.starting_price = ""
            self.duration_in_hours = ""

    def get_ICXTransfer(self) -> str:
        txResult = icon_service.get_transaction_result(self.txHash)
        icx_amt = ""
        if txResult["status"] == 1: #success
            for x in txResult["eventLogs"]:
                if x["scoreAddress"] == NebulaPlanetTokenCx:
                    if "ICXTransfer(Address,Address,int)" in x["indexed"]:
                        icx_amt = f'{hex_to_int(x["indexed"][3]) / 10 ** 18 :.2f} ICX'
        return icx_amt
