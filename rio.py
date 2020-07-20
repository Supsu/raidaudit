import requests
from dotenv import load_dotenv
import os


class RIO:
    """Module that handles communicating with raider.io API

    Module gets region, realm and guild from ENV. It uses those
    values in combination with character names for some methods
    to get mythic+ and raid data to display on site.

    Attributes:
        _region: Region read from ENV
        _realm: Realm read from ENV
        _guild: Guild read from ENV
    """

    _region = ""
    _realm = ""
    _guild = ""

    def __init__(self):
        load_dotenv()
        self._realm = os.getenv("WOWREALM")
        self._region = os.getenv("WOWREGION")
        self._guild = os.getenv("WOWGUILD")

    def getProfile(self, charname: str):
        """Gets a single characters profile from raider.io

        Args:
            charname: string containing name of the character being queried

        Returns:
            A profile of a single character as returned by requests.json()
        """
        url = "https://raider.io/api/v1/characters/profile?"
        url = url + "region=" + self._region
        url = url + "&realm=" + self._realm
        url = url + "&name=" + charname
        url = url + "&fields=mythic_plus_weekly_highest_level_runs,\
            mythic_plus_scores_by_season:current"

        r = requests.get(url)
        return r.json()

    def getRaidProgress(self):
        """Gets raid progress data from raider.io

        Gets raid progress data from raider.io for guild set in
        config/env. Does not require any args. Returns a list of
        dicts following the format below:
        singleraid = {
                    "name": raid,
                    "normalperc": 0,
                    "normalprog": 0,
                    "heroicperc": 0,
                    "heroicprog": 0,
                    "mythicperc": 0,
                    "mythicprog": 0
                }
        Where "name" contains the name of the raid in slug format
        (i.e. hellfire-citadel or crucible-of-storms), and percentage
        and progression values for each difficulty. 
        
        <difficulty>prog comes from Raider.io API and is
        formatted into a string following format "<amount
        of bosses defeated>/<total amount of bosses>". 
        
        <difficulty>perc is instead a float value calculated
        with the same formula as the prog string.

        Returns: 
            raids: list containing dicts

        Raises:
            requests.exceptions.RequestException:
                This is a exception having multiple inheriting exceptions,
                including HTTPError, Timeout and ConnectionError, which all
                basically require calling module to try again, so they are
                not handled in this method.
        """

        def sorter(item):
            """
            Sort raids by their release date.

            Since there doesn't seem to be a good API to get
            raid releases in order, this sorter has to
            be manually updated.

            TODO try handling sorting somehow with battle.net journal api
            """
            roleprio = 9999
            raidlist = {
                "uldir": 800,
                "crucible-of-storms": 805,
                "battle-of-dazaralor": 810,
                "the-eternal-palace": 820,
                "nyalotha-the-waking-city": 830
            }

            if item["name"] in raidlist:
                roleprio = raidlist[item["name"]]

            return (roleprio, item["name"])

        url = "https://raider.io/api/v1/guilds/profile?region=" +\
            self._region + "&realm=" + self._realm + "&name=" + self._guild
        url = url + "&fields=raid_progression"

        # TODO create cache to database so app doesn't query
        # API every time the page is loaded
        r = ""
        try:
            r = requests.get(url)
            r.raise_for_status()
            r = r.json()
        except requests.exceptions.RequestException as err:
            print("Exception in rio.getRaidProgress with Requests: " + repr(err))
            print("Raising exception to calling module, please try again")
            raise
        except ValueError as err:
            print("Exception in rio.getRaidProgress with JSON conversion: " + repr(err))
            print("Returning empty list")
            return []

        raids = []

        try:
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

                tmp["normalprog"] = str(
                    r["raid_progression"][raid]["normal_bosses_killed"]
                    ) + "/" + str(totalbosses)

                tmp["normalperc"] = int(
                    r["raid_progression"][raid]["normal_bosses_killed"]
                    ) / int(totalbosses) * 100

                tmp["heroicprog"] = str(
                    r["raid_progression"][raid]["heroic_bosses_killed"]
                    ) + "/" + str(totalbosses)

                tmp["heroicperc"] = int(
                    r["raid_progression"][raid]["heroic_bosses_killed"]
                    ) / int(totalbosses) * 100

                tmp["mythicprog"] = str(
                    r["raid_progression"][raid]["mythic_bosses_killed"]
                    ) + "/" + str(totalbosses)

                tmp["mythicperc"] = int(
                    r["raid_progression"][raid]["mythic_bosses_killed"]
                    ) / int(totalbosses) * 100

                raids.append(tmp)

        except KeyError as err:
            print("KeyError handling response data in rio.getRaidProgress: " + repr(err))
            print("Returning empty list")
            return []

        # sort by raid release patch, newest (biggest patch number) first
        raids = sorted(raids, key=sorter, reverse=True)

        # TODO see if battle.net API allows getting
        # proper display names for zones with slugs

        return raids


if __name__ == "__main__":
    rio = RIO()
    rio.getRaidProgress()
