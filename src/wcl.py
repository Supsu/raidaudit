import json
from dotenv import load_dotenv
import os
import requests
import time

class WCL:
    
    _key = ""
    _region = ""
    _realm = ""
    _guild = ""
    _urlbase = "https://www.warcraftlogs.com/v1"
    _logRefreshTime = 0

    def __init__(self):
        load_dotenv()
        self._key = os.getenv("WCLKEY")
        self._region = os.getenv("WOWREGION")
        self._realm = os.getenv("WOWREALM")
        self._guild = os.getenv("WOWGUILD")

    def getGuildLogs(self):
        url = self._urlbase + "/reports/guild/"
        url = url + self._guild + "/"
        url = url + self._realm + "/"
        url = url + self._region
        url = url + "?api_key=" + self._key


        r = requests.get(url)

        print(r.url)

        self._logRefreshTime = time.time()

        return r.json()

    def getPlayerAvg(self,player):
        #https://www.warcraftlogs.com:443/v1/rankings/character/supsu/stormscale/eu?metric=dps


        url = self._urlbase + "/rankings/character/"
        url = url + player + "/" + self._realm + "/" + self._region
        url = url + "?metric=dps&api_key=" + self._key

        r = requests.get(url)

        return r.json()


if __name__ == "__main__":
    print("Testing WCL")
    wcl = WCL()
    print(wcl.getGuildLogs())
    print(wcl.getPlayerAvg("Supsu"))
