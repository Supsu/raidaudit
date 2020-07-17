import operator
from dataclasses import dataclass
import datetime

@dataclass
class LootItemData:
    """
    Contains data about a loot item in an RClootcouncil session.
    """
    item_name: str = "<insert name here>"
    recipient: str = ""
    recipient_class: str = ""
    received_time: datetime = None
    original_owner: str = ""
    response: str = ""
    boss_name: str = ""
    instance_name: str = ""
    item_id: int = 0
    item_url: str = ""
    realm_name: str = "Stormscale"

    def __post_init__(self):
        """
        Remove realm names from characters from the same realm but leave them for PUGs.
        """
        if self.realm_name in self.recipient:
            self.recipient = self.recipient.replace("-" + self.realm_name, '')
        if self.realm_name in self.original_owner:
            self.original_owner = self.original_owner.replace("-" + self.realm_name, '')

    def __str__(self):
        """
        String representation of the loot item for easier handling.
        """
        if self.recipient != self.original_owner:
            name = f"{self.original_owner} <br>-> {self.recipient}"
        else:
            name = f"{self.recipient}"
        return f"{self.received_time.strftime('%d.%m %H:%M')}: " +\
                f"{name} received {self.item_url} / " +\
                f"{self.item_name} with response {self.response} " +\
                f"from {self.boss_name} in {self.instance_name}"
