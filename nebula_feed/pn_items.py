from nebula_feed import config, icx_tx

PNItemDict = {
    #0: {"Type": "", "Name": "", "ImageUrl": ""},
    6: {"Type": "CONSUMABLES", "Name": "Bonus Funding", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/bonus-funding.png"},
    7: {"Type": "CONSUMABLES", "Name": "Bonus Supplies", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/bonus-supplies.png"},
    5: {"Type": "CONSUMABLES", "Name": "Catalytic Chip", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/catalytic-chip.png"},
    3: {"Type": "CONSUMABLES", "Name": "Portable Hyperscan", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/portable-hyperscan.png"},
    4: {"Type": "CONSUMABLES", "Name": "Regenerative Nanopaste", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/regenerative-nanopaste.png"},
    9: {"Type": "BLUEPRINTS", "Name": "Abnormality Detector", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/blueprint.png"},
    11: {"Type": "BLUEPRINTS", "Name": "Ceres Autocannon", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/blueprint.png"}
}

class PNItem:
    def __init__(self, txInfo: icx_tx.TxInfo, tokenInfo: dict) -> None:
        # obfuscate address
        self.address = txInfo.address[:8] + ".." + txInfo.address[34:]

        tokenId = txInfo.tokenId

        if tokenId == 0 and txInfo.method == "cancelOrder":
            tokenId = int(tokenInfo["_tokenId"], 16)
        
        # get common attributes
        self.type = self.getItemInfo(tokenId, "Type")
        self.name = self.getItemInfo(tokenId, "Name")
        self.image_url = self.getItemInfo(tokenId, "ImageUrl")
        self.timestamp = txInfo.timestamp
        self.discord_webhook = config.discord_items_webhook
        self.isClaimed = False
        self.info = "\n"

        # collect building blocks for discord embed
        if txInfo.method == "createSellOrder":
            self.title = "Sale order created!"
            self.footer = "Created on "
            self.info += "\nSeller: " + self.address
            self.info += "\nPrice: " + txInfo.set_price
            self.info += "\nAmount: " + txInfo.amount
        elif txInfo.method == "createBuyOrder":
            self.title = "Buy order created!"
            self.footer = "Created on "
            self.info += "\nBuyer: " + self.address
            self.info += "\nPrice: " + txInfo.set_price
            self.info += "\nAmount: " + txInfo.amount
        elif txInfo.method == "buyTokens":
            self.title = "Items bought!"
            self.footer = "Bought on "
            self.info += "\nBuyer: " + self.address
            self.info += "\nPrice: " + txInfo.cost
            self.info += "\nAmount: " + txInfo.amount
            self.info += "\nSold by: " + str(tokenInfo["_maker"])[:8] + ".." + str(tokenInfo["_maker"])[34:]
        elif txInfo.method == "sellTokens":
            self.title = "Items sold!"
            self.footer = "Sold on "
            self.info += "\nBuyer: " + str(tokenInfo["_maker"])[:8] + ".." + str(tokenInfo["_maker"])[34:]
            self.info += "\nPrice: " + f'{int(tokenInfo["_price"], 16) / 10 ** 18 :.2f} ICX'
            self.info += "\nAmount: " + txInfo.amount
            self.info += "\nSold by: " + self.address
        elif txInfo.method == "cancelOrder":
            self.title = str(tokenInfo["_type"]).title() + " order cancelled!"
            self.footer = "Cancelled on "
            self.info += "\nOwner: " + self.address
            self.info += "\nPrice: " + f'{int(tokenInfo["_price"], 16) / 10 ** 18 :.2f} ICX'
            self.info += "\nAmount: " + str(int(tokenInfo["_amount"], 16))

    def getItemInfo(self, tokenId: int, attrib: str) -> str:
        res = ""
        for t_id in PNItemDict.keys():
            if t_id == tokenId:
                res = PNItemDict[t_id][attrib]
                break
        return res

    def generate_discord_info(self) -> str:
        # create discord info output
        # markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
        info = "**" + self.name + "**"
        info += "\n*" + self.type.lower() + "*"
        info += "\n"
        info += self.info
        return info

    def set_color(self) -> str:
        color = "808B96" #default: gray
        if self.type == "CONSUMABLES":
            color = "FDFEFE" #white
        elif self.type == "MATERIALS":
            color = "FDFEFE" #white
        elif self.type == "COMPONENTS":
            color = "FDFEFE" #white
        elif self.type == "BLUEPRINTS":
            color = "3498DB" #blue
        elif self.type == "COLLECTIBLES":
            color = "F39C12" #orange
        elif self.type == "ZONES":
            color = "E74C3C" #red
        return color
