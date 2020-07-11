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

        return r.text

    def getPlayerAvg(self,player):
        #https://www.warcraftlogs.com:443/v1/rankings/character/supsu/stormscale/eu?metric=dps


        url = self._urlbase + "/rankings/character/"
        url = url + player + "/" + self._realm + "/" + self._region
        url = url + "?api_key=" + self._key

        r = requests.get(url).json()

        percentiles = { 3: [],
                        4: [],
                        5: [],
                        "avgN": 0,
                        "avgH": 0,
                        "avgM": 0
                        }
        count = 0

        if len(r) == 0:
            pass
        else:
            for rank in r:
                
                # get parses for N/H/M raids
                if int( rank["difficulty"] ) == 3:
                    percentiles[3].append(float(rank["percentile"]))

                elif int( rank["difficulty"] ) == 4:
                    percentiles[4].append(float(rank["percentile"]))

                elif int( rank["difficulty"] ) == 5:
                    percentiles[5].append(float(rank["percentile"]))

                else:
                    # don't do anything with other difficulty values
                    pass

            # calculate averages
            if len(percentiles[3]) != 0:
                percentiles["avgN"] = sum(percentiles[3]) / len(percentiles[3])

            if len(percentiles[4]) != 0:
                percentiles["avgH"] = sum(percentiles[4]) / len(percentiles[4])

            if len(percentiles[5]) != 0:
                percentiles["avgM"] = sum(percentiles[5]) / len(percentiles[5])


        return percentiles

if __name__ == "__main__":
    print("Testing WCL")
    wcl = WCL()
    print(wcl.getPlayerAvg("Surlo"))
