import json
import requests
from dotenv import load_dotenv
import os

class RIO:

    _region = ""
    _realm = ""
    
    def __init__(self):
        load_dotenv()
        self._realm = os.getenv("WOWREALM")
        self._region = os.getenv("WOWREGION")


    def getProfile(self, charname: str):
        url = "https://raider.io/api/v1/characters/profile?"
        url = url + "region=" + self._region
        url = url + "&realm=" + self._realm
        url = url + "&name=" + charname
        url = url + "&fields=mythic_plus_weekly_highest_level_runs,mythic_plus_scores_by_season:current"

        r = requests.get(url)
        return r.json()


if __name__ == "__main__":
    print("Testing RIO")
    rio = RIO()
    print(rio.getMplus("pirimake"))