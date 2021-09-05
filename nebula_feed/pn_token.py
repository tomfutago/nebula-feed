import json

# Project Nebula contracts
NebulaPlanetTokenCx = "cx57d7acf8b5114b787ecdd99ca460c2272e4d9135"
NebulaSpaceshipTokenCx = "cx943cf4a4e4e281d82b15ae0564bbdcbf8114b3ec"

class PNToken:
    def __init__(self, contract: str, txInfo: dict, tokenInfo: json) -> None:
        self.contract = contract
        
        # obfuscate address
        self.address = txInfo["address"][:8] + ".." + txInfo["address"][34:]
        
        # get common attributes
        self.generation = str(tokenInfo["generation"])
        self.type = str(tokenInfo["type"]).strip()
        self.image_url = tokenInfo["image"]
        self.external_link = tokenInfo["external_link"]

        self.info = "\n"

        if txInfo["method"] == "create_auction":
            self.title = "On auction now!"
            self.footer = "Auctioned on "
            self.info += "\nSeller: " + self.address
            self.info += "\nStarting price: " + txInfo["starting_price"]
            self.info += "\nDuration: " + txInfo["duration_in_hours"] + "hrs"
        elif txInfo["method"] == "list_token":
            self.title = "On sale now!"
            self.footer = "Put on sale on "
            self.info += "\nSeller: " + self.address
            self.info += "\nSet price: " + txInfo["set_price"]
        elif txInfo["method"] == "place_bid":
            self.title = "Bid placed!"
            self.footer = "Bid placed on "
            self.info += "\nBidder: " + self.address
            self.info += "\nPrice: " + txInfo["cost"]
        elif txInfo["method"] == "purchase_token":
            self.title = "Sold!"
            self.footer = "Sold on "
            self.info += "\nNew owner: " + self.address
            self.info += "\nPrice: " + txInfo["cost"]
        
        self.info += "\n[Check it out here](" + self.external_link + ")"

class Planet(PNToken):
    def __init__(self, contract: str, txInfo: dict, tokenInfo: json) -> None:
        super().__init__(contract, txInfo, tokenInfo)

        # get basic info about the token per token type
        if self.contract == NebulaPlanetTokenCx:
            self.name = str(tokenInfo["name"])
            self.rarity = str(tokenInfo["rarity"])
            self.credits = str(tokenInfo["credits"])
            self.industry = str(tokenInfo["industry"])
            self.research = str(tokenInfo["research"])
            
            # any special resources?
            special_resources = []
            for special in tokenInfo["specials"]:
                special_resources.append(str(special["name"]))
            self.specials = ', '.join(special_resources)

    def set_income(self):
        return self.credits + "<:Credit:>/" + self.industry + "<:Industry:>/" + self.research + "<:Research:>"

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
    def __init__(self, contract: str, txInfo: dict, tokenInfo: json) -> None:
        super().__init__(contract, txInfo, tokenInfo)

        if contract == NebulaSpaceshipTokenCx:
            self.name = str(tokenInfo["model_name"])
            self.rarity = str(tokenInfo["set_type"])
            self.tier = str(tokenInfo["tier"])
            self.exploration = str(tokenInfo["exploration"])
            self.colonization = str(tokenInfo["colonization"])
            self.movement = str(tokenInfo["movement"])
            self.fuel = str(tokenInfo["fuel"])

    def set_modifiers(self):
        return self.exploration + "E / " + self.colonization + "C / " + self.movement + "M / " + self.fuel + "F"

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
        if rarity == "CORE":
            color = "3498DB" #blue
        elif rarity == "LORE`":
            color = "E74C3C" #red
        return color
