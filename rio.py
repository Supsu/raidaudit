import json
import requests
from dotenv import load_dotenv
import os

class RIO:

    _region = ""
    _realm = ""
    _guild = ""
    
    def __init__(self):
        load_dotenv()
        self._realm = os.getenv("WOWREALM")
        self._region = os.getenv("WOWREGION")
        self._guild = os.getenv("WOWGUILD")


    def getProfile(self, charname: str):
        url = "https://raider.io/api/v1/characters/profile?"
        url = url + "region=" + self._region
        url = url + "&realm=" + self._realm
        url = url + "&name=" + charname
        url = url + "&fields=mythic_plus_weekly_highest_level_runs,mythic_plus_scores_by_season:current"

        r = requests.get(url)
        return r.json()

    def getRaidProgress(self):
        """
        """

        def sorter(item):
            """
            Sort raids by their release date.

            Since there doesn't seem to be a good API to get raid releases in order,
            this sorter has to be manually updated. 

            TODO try handling sorting somehow with battle.net journal api
            """
            roleprio = 9999
            raidlist = {
                "uldir": 800,
                "crucible-of-storms":805,
                "battle-of-dazaralor":810,
                "the-eternal-palace":820,
                "nyalotha-the-waking-city":830
            }


            if item["name"] in raidlist:
                roleprio = raidlist[item["name"]]
            

            return (roleprio, item["name"])

        url = "https://raider.io/api/v1/guilds/profile?region=" + self._region + "&realm=" + self._realm + "&name=" + self._guild
        url = url + "&fields=raid_progression"

        # TODO create cache to database so app doesn't query API every time the page is loaded

        r = requests.get(url).json()

        raids = []

        for raid in r["raid_progression"]:
            """
            Creates dict entities that have the data wanted for display
            """
            tmp = {
                "name": raid,
                "normalperc": 0,
                "normalprog": 0,
                "heroicperc": 0,
                "heroicprog": 0,
                "mythicperc": 0,
                "mythicprog": 0
            }

            totalbosses = r["raid_progression"][raid]["total_bosses"]

            tmp["normalprog"] = str(r["raid_progression"][raid]["normal_bosses_killed"]) + "/" + str(totalbosses)
            tmp["normalperc"] = int(r["raid_progression"][raid]["normal_bosses_killed"]) / int(totalbosses) *100

            tmp["heroicprog"] = str(r["raid_progression"][raid]["heroic_bosses_killed"]) + "/" + str(totalbosses)
            tmp["heroicperc"] = int(r["raid_progression"][raid]["heroic_bosses_killed"]) / int(totalbosses) *100

            tmp["mythicprog"] = str(r["raid_progression"][raid]["mythic_bosses_killed"]) + "/" + str(totalbosses)
            tmp["mythicperc"] = int(r["raid_progression"][raid]["mythic_bosses_killed"]) / int(totalbosses) *100

            raids.append(tmp)


        

        # sort by raid release patch, newest (biggest patch number) first
        raids = sorted(raids, key=sorter, reverse=True)

        # TODO see if battle.net API allows getting proper display names for zones with slugs


        return raids

if __name__ == "__main__":
    rio = RIO()
    rio.getRaidProgress()