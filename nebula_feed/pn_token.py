import os
import json
import icx_tx
from dotenv import load_dotenv

# load env variables
is_heroku = os.getenv("IS_HEROKU", None)
if not is_heroku:
    load_dotenv()

# custom emoji IDs - removed as discord complains about excedding API rate limits
#credits_emoji = os.getenv("credits_emoji")
#industry_emoji = os.getenv("industry_emoji")
#research_emoji = os.getenv("research_emoji")
# todo: add ship modifiers once available on official PN discord


class PNToken:
    def __init__(self, txInfo: icx_tx.TxInfo, tokenInfo: json) -> None:
        # obfuscate address
        self.address = txInfo.address[:8] + ".." + txInfo.address[34:]
        
        # get common attributes
        self.generation = str(tokenInfo["generation"])
        self.type = str(tokenInfo["type"]).strip()
        self.image_url = tokenInfo["image"]
        self.external_link = tokenInfo["external_link"]
        self.timestamp = txInfo.timestamp
        self.info = "\n"

        # set destination discord channel
        if txInfo.method == "claim_token" or txInfo.method == "transfer":
            self.discord_webhook = os.getenv("DISCORD_CLAIMED_WEBHOOK")
        else:
            self.discord_webhook = os.getenv("DISCORD_MARKET_WEBHOOK")

        # collect building blocks for discord embed
        if txInfo.method == "claim_token" or txInfo.method == "transfer":
            self.title = "Claimed!"
            self.footer = "Claimed on "
            self.info += "\nHappy owner: " + self.address
            self.info += "\nClaimed for: "
            self.info += txInfo.cost if float(txInfo.cost) > 0 else "credits"
        elif txInfo.method == "create_auction":
            self.title = "On auction now!"
            self.footer = "Auctioned on "
            self.info += "\nSeller: " + self.address
            self.info += "\nStarting price: " + txInfo.starting_price
            self.info += "\nDuration: " + txInfo.duration_in_hours + "hrs"
        elif txInfo.method == "list_token":
            self.title = "On sale now!"
            self.footer = "Put on sale on "
            self.info += "\nSeller: " + self.address
            self.info += "\nSet price: " + txInfo.set_price
        elif txInfo.method == "place_bid":
            self.title = "Bid placed!"
            self.footer = "Bid placed on "
            self.info += "\nBidder: " + self.address
            self.info += "\nPrice: " + txInfo.cost
        elif txInfo.method == "purchase_token":
            self.title = "Sold!"
            self.footer = "Sold on "
            self.info += "\nNew owner: " + self.address
            self.info += "\nPrice: " + txInfo.cost
        elif txInfo.method == "finalize_auction":
            self.title = "Auction finalized!"
            self.footer = "Finalized on "
            self.info += "\nNew owner: " + self.address
        elif txInfo.method == "return_unsold_item":
            self.title = "Unsold and returned :("
            self.footer = "Returned on "
            self.info += "\nOwner: " + self.address
        elif txInfo.method == "delist_token":
            self.title = "Delisted!"
            self.footer = "Delisted on "
            self.info += "\nOwner: " + self.address
        
        self.info += "\n[Check it out here](" + self.external_link + ")"

class Planet(PNToken):
    def __init__(self, txInfo: icx_tx.TxInfo, tokenInfo: json) -> None:
        super().__init__(txInfo, tokenInfo)

        # get basic info about the token per token type
        self.name = str(tokenInfo["name"])
        self.rarity = str(tokenInfo["rarity"])
        self.credits = str(tokenInfo["credits"])
        self.industry = str(tokenInfo["industry"])
        self.research = str(tokenInfo["research"])

        # check name for claimed planets
        if self.name.upper() == "UNDISCOVERED PLANET":
            self.isUndiscovered = True
            self.discord_webhook = os.getenv("DISCORD_LOG_WEBHOOK")
        else:
            self.isUndiscovered = False
        
        # any special resources?
        special_resources = []
        for special in tokenInfo["specials"]:
            special_resources.append(str(special["name"]))
        self.specials = ', '.join(special_resources)

    def set_income(self):
        #return credits_emoji + self.credits + industry_emoji + self.industry + research_emoji + self.research
        return "C" + self.credits + " I" + self.industry + " R" + self.research

    def generate_discord_info(self) -> str:
        # create discord info output
        # markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
        info = "**" + self.name.upper() + "**"
        info += "\n" + self.rarity.upper() + " / " + self.generation.upper()
        info += "\n"
        info += "\nType: " + self.type.lower().strip()
        info += "\nIncome: " + self.set_income()

        if len(self.specials) > 0:
            info += "\nSpecials: " + self.specials
        
        info += self.info
        return info

    def set_color(self) -> str:
        rarity = self.rarity.upper()
        color = "808B96" #default: gray
        if rarity == "COMMON":
            color = "808B96" #gray
        elif rarity == "UNCOMMON":
            color = "FDFEFE" #white
        elif rarity == "RARE":
            color = "3498DB" #blue
        elif rarity == "LEGENDARY":
            color = "8E44AD" #purple
        elif rarity == "MYTHIC":
            color = "F39C12" #orange
        return color

class Spaceship(PNToken):
    def __init__(self, txInfo: icx_tx.TxInfo, tokenInfo: json) -> None:
        super().__init__(txInfo, tokenInfo)

        self.name = str(tokenInfo["model_name"])
        self.rarity = str(tokenInfo["set_type"])
        self.tier = str(tokenInfo["tier"])
        self.exploration = str(tokenInfo["exploration"])
        self.colonization = str(tokenInfo["colonization"])
        self.movement = str(tokenInfo["movement"])
        self.fuel = str(tokenInfo["fuel"])
        self.isUndiscovered = False

    def set_modifiers(self):
        return "E" + self.exploration + " C" + self.colonization + " M" + self.movement + " F" + self.fuel

    def generate_discord_info(self) -> str:
        # create discord info output
        # markdown options: *Italic* **bold** __underline__ ~~strikeout~~ [hyperlink](https://google.com) `code`
        info = "**" + self.name.upper() + "**"
        info += "\n" + self.generation.upper()
        info += "\n"
        info += "\nType: " + self.type.lower().strip() + " " + self.tier.upper()
        info += "\nModifiers: " + self.set_modifiers()
        info += self.info
        return info

    def set_color(self) -> str:
        rarity = self.rarity.upper()
        color = "808B96" #default: gray
        if rarity == "CORE":
            color = "3498DB" #blue
        elif rarity == "LORE`":
            color = "E74C3C" #red
        return color
