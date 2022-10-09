import json
from nebula_feed import config, icx_tx

class PNItem:
    def __init__(self, txInfo: icx_tx.TxInfo, tokenInfo: json, orderInfo: dict) -> None:
        # obfuscate address
        self.address = txInfo.address[:8] + ".." + txInfo.address[34:]

        # get common attributes
        self.type = str(tokenInfo["type"])
        self.name = str(tokenInfo["name"])
        self.description = str(tokenInfo["flavor_text"])
        self.image_url = "https://d2r1p2wt01zdse.cloudfront.net/icons/" + str(tokenInfo["image_path"])
        self.timestamp = txInfo.timestamp
        self.discord_webhook = [config.discord_items_webhook, config.discord_items_webhook_2]
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
            self.info += "\nSold by: " + str(orderInfo["_maker"])[:8] + ".." + str(orderInfo["_maker"])[34:]
        elif txInfo.method == "sellTokens":
            self.title = "Items sold!"
            self.footer = "Sold on "
            self.info += "\nBuyer: " + str(orderInfo["_maker"])[:8] + ".." + str(orderInfo["_maker"])[34:]
            self.info += "\nPrice: " + f'{int(orderInfo["_price"], 16) / 10 ** 18 :.2f} ICX'
            self.info += "\nAmount: " + txInfo.amount
            self.info += "\nSold by: " + self.address
        elif txInfo.method == "cancelOrder":
            self.title = str(orderInfo["_type"]).title() + " order cancelled!"
            self.footer = "Cancelled on "
            self.info += "\nOwner: " + self.address
            self.info += "\nPrice: " + f'{int(orderInfo["_price"], 16) / 10 ** 18 :.2f} ICX'
            self.info += "\nAmount: " + str(int(orderInfo["_amount"], 16))

    def generate_discord_info(self) -> str:
        # create discord info output
        # markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
        info = "**" + self.name + "**"
        info += "\n*" + self.type.lower() + "*"
        info += "\n"
        info += "\n" + self.description
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
