import json
import requests
from datetime import datetime
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.exception import JSONRPCException

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaSpaceshipTokenCx = "cx943cf4a4e4e281d82b15ae0564bbdcbf8114b3ec"


# connect to ICON main-net
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io", 3))

class IcxBlock:
    def __init__(self, block: int) -> None:
        block = icon_service.get_block(block)

    def get_latest_block(self):
        latest_block = icon_service.get_block("latest")
        return latest_block

    def get_block(self, block: int):
        block = icon_service.get_block(block)
        return block

class TxInfo:
    def __init__(self, tx: json) -> None:
        self.txHash = tx["txHash"]
        self.address = tx["from"]
        #self.timestamp = datetime.fromtimestamp(tx["timestamp"] / 1000000).replace(microsecond=0).isoformat()
        self.timestamp = int(tx["timestamp"] / 1000000)
        self.cost = str(int(tx["value"]) / 10 ** 18)
        self.method = tx["data"]["method"]
        self.tokenId = int(tx["data"]["params"]["_token_id"], 16)
        
    def get_tx_result(self, tx_hash: str):
        tx_result = icon_service.get_transaction_result(tx_hash)
        return tx_result

    def call(self, to, method, params=None):
        try:
            call = CallBuilder().to(to).method(method).params(params).build()
            result = icon_service.call(call)
            return result
        except JSONRPCException as e:
            raise Exception(e)
