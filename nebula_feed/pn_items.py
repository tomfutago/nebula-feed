from nebula_feed import config, icx_tx

PNItemDict = {
    #0: {"Type": "", "Name": "", "ImageUrl": ""},
    6: {"Type": "CONSUMABLES", "Name": "Bonus Funding", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/bonus-funding.png"},
    7: {"Type": "CONSUMABLES", "Name": "Bonus Supplies", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/bonus-supplies.png"},
    1: {"Type": "CONSUMABLES", "Name": "Catalytic Chip", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/catalytic-chip.png"},
    3: {"Type": "CONSUMABLES", "Name": "Portable Hyperscan", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/portable-hyperscan.png"},
    4: {"Type": "CONSUMABLES", "Name": "Regenerative Nanopaste", "ImageUrl": "https://d2r1p2wt01zdse.cloudfront.net/icons/regenerative-nanopaste.png"}
}

class PNItem:
    def __init__(self, txInfo: icx_tx.TxInfo) -> None:
        # obfuscate address
        self.address = txInfo.address[:8] + ".." + txInfo.address[34:]
        
        # get common attributes
        self.type = self.getItemInfo(txInfo.tokenId, "Type")
        self.name = self.getItemInfo(txInfo.tokenId, "Name")
        self.image_url = self.getItemInfo(txInfo.tokenId, "ImageUrl")
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
        elif txInfo.method == "sellTokens":
            self.title = "Tokens sold!"
            self.footer = "Sold on "
            self.info += "\nSeller: " + self.address
            self.info += "\nPrice: " + txInfo.set_price
            self.info += "\nAmount: " + txInfo.amount
        elif txInfo.method == "buyTokens":
            self.title = "Tokens bought!"
            self.footer = "Bought on "
            self.info += "\nBuyer: " + self.address
            self.info += "\nPrice: " + txInfo.set_price
            self.info += "\nAmount: " + txInfo.amount

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
        info = "**" + self.type + "**"
        info += "\n" + self.name
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
