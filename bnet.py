import time
from typing import Dict, List, Union

import requests
from dotenv import load_dotenv
import os
import json


class Bnet:
    _id: str = ""
    _secret: str = ""
    _token: str = ""
    _expires: int = 0
    _timestamp: float = 0
    _region: str = ""
    _guild: str = ""
    _realm: str = ""
    _apiurl: str = ""
    _namespace: str = ""
    _locale: str = ""
    _raiderrank: int = 0

    _CLASSID: Dict[int, str] = {
            1: "Warrior",
            2: "Paladin",
            3: "Hunter",
            4: "Rogue",
            5: "Priest",
            6: "Death Knight",
            7: "Shaman",
            8: "Mage",
            9: "Warlock",
            10: "Monk",
            11: "Druid",
            12: "Demon Hunter"
        }

    def __init__(self):
        self._timestamp = time.time()

        load_dotenv()

        self._raiderrank = int(os.getenv("RAIDERRANK"))
        self._region = os.getenv("WOWREGION")
        self._guild = os.getenv("WOWGUILD")
        self._realm = os.getenv("WOWREALM")
        self._id = os.getenv("BNETID")
        self._secret = os.getenv("BNETSECRET")
        self._namespace = os.getenv("WOWNAMESPACE")
        self._locale = os.getenv("WOWLOCALE")
        self._apiurl = "https://" + self._region + ".api.blizzard.com/"

    def getAccessToken(self) -> str:
        """
        Get access token with given id and secret
        """
        print("Checking access token..")

        checkurl = "https://" + self._region + ".battle.net/oauth/check_token"
        r = requests.post(checkurl, data={"token": self._token})

        # if "error" not in r:
        # return self._token

        print("Getting new access token for battle.net API")
        # get new token
        tokenurl = "https://" + self._region + ".battle.net/oauth/token"
        r = requests.post(tokenurl, auth=(self._id, self._secret), data={
            "grant_type": "client_credentials"
            })
        print(str(r.status_code))
        if str(r.status_code) != str(200):
            print("ERROR " + str(r.status_code))
            print("R: " + r)
            return "ERROR " + str(r.status_code)
        data = r.json()
        self._token = data["access_token"]
        self._expires = int(data["expires_in"])
        return self._token

    def getRoster(self):
        """
        Gets guild roster from b.net API to automatically add raiders
        """
        print("Getting roster..")
        self._token = self.getAccessToken()
        reqUrl = self._apiurl + "data/wow/guild/" +\
            self._realm + "/" + self._guild + "/roster?namespace=" +\
            self._namespace + "&locale=" + self._locale +\
            "&access_token=" + self._token

        try:
            roster = requests.get(reqUrl)
            if roster.status_code == 504:
                raise TimeoutError("HTTP 504")
        except TimeoutError as err:
            print("bnet.getRoster TimeoutError " + repr(err))
            return {}

        print("bnet.GetRoster " + str(roster.status_code))
        try:
            roster = roster.json()
        except json.decoder.JSONDecodeError as err:
            print("bnet.getRoster JSONDecodeError " + repr(err))
            return {}
        except Exception as err:
            print("bnet.getRoster Exception " + repr(err))
            return {}

        result = []

        members = roster["members"]

        for character in members:
            tmp = {
                "name": "",
                "class": ""
                }
            rank = character["rank"]
            if rank != self._raiderrank:
                # not the right rank, skipping
                continue
            else:
                tmp["name"] = character["character"]["name"]
                tmp["class"] = self._CLASSID[
                    character[
                        "character"
                        ][
                            "playable_class"
                            ][
                                "id"]
                                ]
                result.append(tmp)
        return result

    def getCharacterProfile(self, charname: str, realm: str = None):
        """
        get profile for a certain character
        """

        if realm is None:
            realm = self._realm

        print("Getting character profile for " + charname + " from " + realm)

        self._token = self.getAccessToken()
        reqUrl = self._apiurl + "profile/wow/character/" + realm + "/" +\
            charname.lower() + "?namespace=" + self._namespace +\
            "&locale=" + self._locale + "&access_token=" + self._token
        print("bnet.getCharacterProfile " + reqUrl)

        req = requests.get(reqUrl)
        print("bnet.getCharacterProfile " + str(req.status_code))
        req = req.json()

        return req

    def getItemName(self, itemid: Union[int, List[int]]):
        """
        Get item name from the bnet endpoint

        Args:
            itemid (int, :obj: `list` of int): item ID or a list of item IDs to query from the endpoint.

        Returns:
            Item name or a list of item names corresponding to the arg item IDs.
        """

        print(f"Getting item name for {itemid}...")

        self._token = self.getAccessToken()
        if not isinstance(itemid, list):
            reqUrl = f"{self._apiurl}data/wow/item/{itemid}?namespace={self._namespace}" \
                     f"&locale={self._locale}&access_token={self._token}"
            print(reqUrl)
            print(f"bnet.getItemName {itemid}")
            req = requests.get(reqUrl)
            print(f"bnet.getItemName {req.status_code}")
            if req.status_code != 200:
                return ""
            else:
                req = req.json()
                return req['name']
        else:
            item_list = []
            for item in itemid:
                reqUrl = f"{self._apiurl}data/wow/item/{item}?namespace={self._namespace}" \
                         f"&locale={self._locale}&access_token={self._token}"
                print(reqUrl)
                print(f"bnet.getItemName {item}")
                req = requests.get(reqUrl)
                print(f"bnet.getItemName {req.status_code}")
                if req.status_code == 200:
                    item_list.append(req.json()['name'])
            return item_list

if __name__ == "__main__":
    print("Running as main, testing..")
    bnet = Bnet()
    print(bnet.getCharacterProfile("Supsu"))
