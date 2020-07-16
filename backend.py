import operator
from dataclasses import dataclass

from typing import Dict, List, Tuple, Union

from datetime import datetime
from db import Database
from bnet import Bnet
from rio import RIO
from wcl import WCL
import json
import time
from dotenv import load_dotenv
import os


@dataclass
class LootItemData:
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
        if self.realm_name in self.recipient:
            self.recipient = self.recipient.replace("-" + self.realm_name, '')
        if self.realm_name in self.original_owner:
            self.original_owner = self.original_owner.replace("-" + self.realm_name, '')

    def __str__(self):

        if self.recipient != self.original_owner:
            name = f"{self.original_owner} >> {self.recipient}"
        else:
            name = f"{self.recipient}"
        return f"{self.received_time.strftime('%d.%m %H:%M')} [{name}] received [url={self.item_url}]" \
                   f"[{self.item_name}][/url] ({self.response}) from {self.boss_name} in {self.instance_name}"


class Backend:
    db = ""
    bnet = ""
    rio = ""
    wcl = ""
    realm = ""
    region = ""

    def __init__(self):
        load_dotenv()
        self.db = Database()
        self.bnet = Bnet()
        self.rio = RIO()
        self.wcl = WCL()
        self.region = os.getenv("WOWREGION")
        self.realm = os.getenv("WOWREALM")

    def getView(self) -> List[Dict[str, str]]:
        """
        Get data for roster table
        """

        def sorter(item) -> Tuple[int, str]:
            roleprio = 0
            if item["Role"] == "Tank":
                roleprio = 1
            elif item["Role"] == "Healer":
                roleprio = 2
            elif item["Role"] == "DPS":
                roleprio = 3
            else:
                roleprio = 4

            return (roleprio, item["name"])

        data = self.db.getIndex()

        listed = sorted(data, key=sorter)

        return listed

    def getBlog(self):
        """
        Get blog posts
        """
        data = self.db.getBlog()
        return data

    def getSingleBlog(self, id: str):
        """
        Get a single blog post with id
        """
        # TODO create a db.py method for getting single blog, this is ugly
        return self.db.db.blog.find_one({"id": id})

    def getLogs(self):
        """
        Get most recent logs for guild from WCL
        """

        data = json.loads(self.wcl.getGuildLogs())

        if "error" in data:
            data = [{"title": "Error!", "start": data["error"], "id": " "}]

        elif len(data) > 10:
            data = data[0:10]

        for row in data:
            row["start"] = time.strftime(
                '%Y-%m-%d', time.localtime(int(row["start"]/1000))
                )

        return data

    def updateView(self):
        """
        Update view tables from db
        """
        pass

    def addPlayer(self, player: Dict[str, str]) -> bool:
        """
        Add player to roster manually
        """

        self.db.addPlayer(player["name"], player["Class"], player["Role"])

        return True

    def removePlayer(self, player: Dict[str, str]) -> bool:
        """
        Remove player from roster
        """
        query = {
            "name": player["name"]
        }

        collection = ""

        if player["automated"]:
            collection = "autoplayers"

        else:
            collection = "players"

        res = self.db.remove(collection, query)

        return res

    def updateRoster(self):
        """
        Update roster data
        """
        # get raiders from bnet
        roster = self.bnet.getRoster()
        manuals = self.db.getManualPlayers()

        print(roster)
        print(manuals)

        # iterate over players and get full data
        for i in roster:
            tmp = {"name": "",
                   "Class": "",
                   "Role": "",
                   "ilv": 0.0,
                   "Weekly": 0,
                   "rio": 0.0,
                   "wcln": 0.0,
                   "wclh": 0.0,
                   "wclm": 0.0
                   }

            name = i["name"]
            cclass = i["class"]

            tmp["name"] = name
            tmp["Class"] = cclass
            tmp["Role"] = self.db.findRole(name)

            print("Getting ilv from battle.net profile for " + name)
            bnetprofile = self.bnet.getCharacterProfile(name)
            tmp["ilv"] = bnetprofile["average_item_level"]

            print("Getting m+ data from raider.io for " + name)
            rioprofile = self.rio.getProfile(name)

            # will return empty list if there are no runs for the week
            if len(rioprofile["mythic_plus_weekly_highest_level_runs"]) == 0:
                tmp["Weekly"] = 0
            else:
                tmp["Weekly"] = int(
                    rioprofile["mythic_plus_weekly_highest_level_runs"][
                        0]["mythic_level"]
                    )

            # in case of no data, should still return 0 as a score
            tmp["rio"] = float(
                rioprofile["mythic_plus_scores_by_season"][0]["scores"]["all"]
                )

            wclperf = self.wcl.getPlayerAvg(name)

            tmp["wcln"] = wclperf["avgN"]
            tmp["wclh"] = wclperf["avgH"]
            tmp["wclm"] = wclperf["avgM"]

            dbquery = {"name": name}
            dbnewdata = {"$set": tmp}

            # push updated automated players to DB
            # TODO create a method for updating in db.py this is ugly
            self.db.db.autoplayers.update_one(dbquery, dbnewdata, upsert=True)

        # TODO refactor this to have only one loop / function call
        # ugly repeating loop

        for i in manuals:
            tmp = {"name": "",
                   "Class": "",
                   "Role": "",
                   "ilv": 0.0,
                   "Weekly": 0,
                   "rio": 0.0,
                   "wcln": 0.0,
                   "wclh": 0.0,
                   "wclm": 0.0
                   }

            name = i["name"]
            cclass = i["Class"]

            tmp["name"] = name
            tmp["Class"] = cclass
            tmp["Role"] = self.db.findRole(name)

            print("Getting ilv from battle.net profile for " + name)
            bnetprofile = self.bnet.getCharacterProfile(name)
            tmp["ilv"] = bnetprofile["average_item_level"]

            print("Getting m+ data from raider.io for " + name)
            rioprofile = self.rio.getProfile(name)
            # will return empty list if there are no runs for the week
            if len(rioprofile["mythic_plus_weekly_highest_level_runs"]) == 0:
                tmp["Weekly"] = 0
            else:
                tmp["Weekly"] = int(
                    rioprofile["mythic_plus_weekly_highest_level_runs"][0]
                    ["mythic_level"]
                    )

            tmp["rio"] = float(
                rioprofile["mythic_plus_scores_by_season"][0]["scores"]["all"]
                )

            wclperf = self.wcl.getPlayerAvg(name)

            tmp["wcln"] = wclperf["avgN"]
            tmp["wclh"] = wclperf["avgH"]
            tmp["wclm"] = wclperf["avgM"]

            dbquery = {"name": name}
            dbnewdata = {"$set": tmp}

            # push updated automated players to DB
            # TODO create a method for updating in db.py this is ugly
            self.db.db.players.update_one(dbquery, dbnewdata, upsert=True)

        # Update updating time to settings
        # TODO this needs methods, ugly
        print("Setting update timestamp to " + str(int(time.time())))
        response = self.db.db.settings.update_one(
            {}, {"$set": {"timestamp": int(time.time())}}, upsert=False
            )
        print("Modified " + str(response.modified_count) + " entries")

        # TODO implement some kind of error handling and return False in
        # case there is an error
        return True

    def login(self, usr: str, pwd: str):
        """
        Check login information
        """

        settings = self.db.getSettings()

        boolusr = False
        boolpwd = False

        # check admin credentials
        if settings["adminname"] == usr:
            boolusr = True
        if settings["adminpwd"] == pwd:
            boolpwd = True

        if boolusr and boolpwd:
            return boolusr, boolpwd
        else:
            # check additional login table for officers etc
            # TODO
            return boolusr, boolpwd

    def post(self, title: str, content: str):
        r = self.db.postBlog(title, content)

        return r

    def getUpdateTimestamp(self):
        return self.db.getSettings()["timestamp"]

    def editPlayerRole(self, playername: str,
                       playerrole: str, automated: bool):
        self.db.updateRole(playername, playerrole, automated)

    def getSideBar(self):
        """
        Gets data for sidebar.

        Initializes a sidebar element list.
        Calls rio.py method getRaidProgress() to get raid progress
        from raider.io

        Returns:
            List of sidebar entities, where [0] is reserved for raid progress
            and [1] for raidaudit version
        """
        sidebar = [{"progress": "NA"}, {"version": "NA"}]

        progress = self.rio.getRaidProgress()
        sidebar[0] = progress
        return sidebar

    def getLinkInfo(self):
        """
        Get realm, region and locale data to generate links to roster table
        """
        info = {
            "locale": "en-gb",
            "region": self.region,
            "realm": self.realm
        }

        # TODO support all regions? now only eu/us
        if info["region"] == "us":
            info["locale"] = "en-us"

        return info

    def getLootLog(self, loot_file: Union[str, List[str]], reversed: bool = True) -> List[LootItemData]:
        """
        Fetches the loot log from exported RClootcouncil file
        :param loot_file:
            Filename, list of filenames or directory containing .json files that contain the loot data
        :param reversed:
            If reversed, loot is sorted in time-ascending order
        :return:
            List containing the rows of BBCode for the equipment log
        """
        # Pull data from file(s)
        pulled_data = []
        if isinstance(loot_file, list):
            for filename in loot_file:
                with open(filename, 'rb') as f:
                    pulled_data += json.load(f)
        elif os.path.isdir(loot_file):
            files = [os.path.join(loot_file, f) for f in os.listdir(loot_file) if
                     os.path.isfile(os.path.join(loot_file, f)) and '.json' in f]
            for file in files:
                with open(file, 'rb') as f:
                    pulled_data += json.load(f)
        elif os.path.isfile(loot_file):
            with open(loot_file, 'rb') as f:
                pulled_data += json.load(f)

        # parse data in file(s)
        loot_list = []
        for loot_data in pulled_data:
            itemstring = loot_data['itemString']
            vals = itemstring.split(':')
            item_id = loot_data['itemID']
            bonuses = vals[14:]
            url = f"https://www.wowhead.com/item={item_id}&bonus={':'.join(bonuses)}"
            date_string = loot_data['date'] + " " + loot_data['time']
            date = datetime.strptime(date_string, '%d/%m/%y %H:%M:%S')
            loot = LootItemData(recipient=loot_data['player'],
                                recipient_class=loot_data['class'],
                                received_time=date,
                                original_owner=loot_data['owner'],
                                response=loot_data['response'],
                                boss_name=loot_data['boss'],
                                instance_name=loot_data['instance'],
                                item_id=loot_data['itemID'],
                                item_url=url,
                                item_name=self.bnet.getItemName(item_id),
                                realm_name="Stormscale")
            loot_list.append(loot)

        loot_list.sort(key=operator.attrgetter('received_time'), reverse=reversed)

        return loot_list


if __name__ == "__main__":
    back = Backend()
    print(back.getUpdateTimestamp())
