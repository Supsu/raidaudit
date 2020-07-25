from typing import Dict, List, Tuple

import pymongo
from dotenv import load_dotenv
import os
import time
from dataclasses import asdict

from attendancedata import AttendanceData
from lootitemdata import LootItemData


class Database:
    dburl = ""
    dbport = ""
    client = ""
    db = ""
    usr = ""
    pwd = ""

    def __init__(self):
        load_dotenv()

        self.dburl = os.getenv("MONGOURL")
        self.dbport = int(os.getenv("MONGOPORT"))
        self.usr = os.getenv("MONGOUSER")
        self.pwd = os.getenv("MONGOPWD")

        self.client = pymongo.MongoClient(
            self.dburl,
            self.dbport,
            username=self.usr,
            password=self.pwd,
            connect=False
            )
        self.db = self.client.raidaudit

        print("Initialized connection to database " + self.db.name)

    def getIndex(self):
        data = []

        # self.db.players.find() + self.db.autoplayers.find()
        for player in self.db.players.find():
            player["automated"] = "manual-player"
            data.append(player)

        for player in self.db.autoplayers.find():
            player["automated"] = "automated-player"
            data.append(player)

        return data

    def getBlog(self):
        return self.db.blog.find().sort("id", pymongo.DESCENDING)

    def getSettings(self):
        return self.db.settings.find_one()

    def postBlog(self, title: str, content: str) -> bool:
        self.db.blog.insert_one(
            {"title": title,
             "content": content,
             "timestamp": time.strftime(
                 '%Y-%m-%d', time.localtime()
                 ),
             "id": int(time.time())})

        # TODO error checking
        return True

    def addPlayer(self, name, charclass, role, automated=False):
        if automated:
            self.db.autoplayers.insert_one(
                {
                    "name": name,
                    "Class": charclass,
                    "Role": role,
                    "ilv": 0.0,
                    "Weekly": 0,
                    "rio": 0.0,
                    "wcln": 0.0,
                    "wclh": 0.0,
                    "wclm": 0.0
                    }
                    )
        else:
            self.db.players.insert_one(
                {
                    "name": name,
                    "Class": charclass,
                    "Role": role, "ilv": 0.0,
                    "Weekly": 0,
                    "rio": 0.0,
                    "wcln": 0.0,
                    "wclh": 0.0,
                    "wclm": 0.0
                    }
                    )

    def getManualPlayers(self):
        return self.db.players.find()

    def updateRole(self, playername, newrole, automated):
        if automated:
            self.db.autoplayers.update_one(
                {"name": playername}, {"$set": {"Role": newrole}}
                )
        else:
            self.db.players.update_one(
                {"name": playername}, {"$set": {"Role": newrole}}
                )

    def findRole(self, player):
        # try automated players first since they are probably majority

        found = self.db.autoplayers.find_one({"name": player})
        if found is not None:
            return found["Role"]
        else:
            found = self.db.players.find_one({"name": player})
            if found is not None:
                return found["Role"]

            else:
                return ""

    def remove(self, collection: str, query: Dict[str, str]) -> bool:

        print("db.remove: query " + str(query))
        print("db.remove: collection " + str(collection))

        if collection == "autoplayers":
            r = self.db.autoplayers.delete_one(query)
            print("Deleted " + str(r.deleted_count) + " items")
            return True

        elif collection == "players":
            r = self.db.players.delete_one(query)
            print("Deleted " + str(r.deleted_count) + " items")
            return True
        else:
            print("db.remove could not find collection")
            return False

    def getLoot(self):
        """Gets Loot entries from DB

        Get all entries in collection "loot" in database.

        Returns:
            res: pymongo cursor to query response
        """

        res = self.db.loot.find(projection={"_id": False})
        return res

    def addLoot(self, newloot: List[LootItemData]) -> bool:
        """Adds new loot data to DB

        A method to insert data parsed to BBCode via backend.getLootLog()
        to database.

        Args:
            newloot: 

        Returns:
            success: bool
        """

        for entry in newloot:
            self.db.loot.insert_one(asdict(entry))

        return True

    def addAttendance(self, wcl_attendance):
        """
        Adds a piece of attendance data into the db if it doesn't exist there yet.

        Args:
            wcl_attendance (dict):
                Contains attendance data from wcl

        Returns:
            True if data was added, False otherwise
        """

        log_id = wcl_attendance['code']
        players = wcl_attendance['players']
        start_time = wcl_attendance['start_time']
        zone_id = wcl_attendance['zone']['id']
        raid_name = wcl_attendance['zone']['name']

        col: pymongo.collection.Collection = self.db['attendance_collection']

        # Ensure that indexing is done
        attendance_index = "attendance_index"
        if attendance_index not in col.index_information():
            print("Creating attendance index...")
            keys = [('tag', pymongo.DESCENDING), ('log_id', pymongo.DESCENDING),
                    ('name', pymongo.DESCENDING), ('benched', pymongo.DESCENDING)]
            col.create_index(keys, name=attendance_index, unique=False, sparse=True)

        raid_index = 'attendance_raid_index'
        if raid_index not in col.index_information():
            print("Creating attendance raid index...")
            keys = [('tag', pymongo.DESCENDING), ('zone_id', pymongo.DESCENDING),
                    ('start_time', pymongo.DESCENDING)]
            col.create_index(keys, name=raid_index, unique=False, sparse=True)

        raid_index = 'attendance_raid_name_index'
        if raid_index not in col.index_information():
            print("Creating attendance raid name index...")
            keys = [('tag', pymongo.DESCENDING), ('raid_name', pymongo.DESCENDING),
                    ('start_time', pymongo.DESCENDING)]
            col.create_index(keys, name=raid_index, unique=False, sparse=True)

        if col.find_one({'tag': 'META', 'log_id':log_id}) is None:
            return False

        datas = []
        metadata = {'tag': 'META', 'log_id': log_id, 'zone_id': zone_id, 'raid_name': raid_name, 'start_time': start_time}
        datas.append(metadata)
        for player in players:
            data = {'tag': 'PLAYER', 'log_id': log_id, 'name': player['name'], 'player_class': player['type']}
            if player['presence'] == 1:
                data['benched'] = False
            elif player['presence'] == 2:
                data['benched'] = True
            datas.append(data)
        result = col.insert_many(datas)

        if len(result) > 0:
            return True
        else:
            return False

    def getAttendanceRaids(self) -> Dict[int, str]:
        """
        Fetches known raid IDs and names from the attendance data

        Returns:
            Dict[int, str] containing raid IDs and their names
        """

        filt = {'tag': 'META'}
        col = self.db['attendance_collection']
        return col.find(filt).distinct('zone_id')

    def getAttendance(self, raid_id: int = None, raid_name: str = None, player_name: str = None):
        """
        Pulls attendance data from DB and forms it into a dictionary of AttendanceData objects. Either Raid ID or
        raid name must be supplied.
        Args:
            raid_id (int):
                ID number of the raid to serach for
            raid_name (string):
                Name of the raid to search for
            player_name (string):
                Name of the player to search for (optional)

        Returns:
            Tuple[int, Dict[str, AttendanceData]]:
                Contains the total amount of raids and the attendance data for each player
        """
        assert raid_id is not None or raid_name is not None, "Either raid id or raid name must be supplised"

        col = self.db['attendance_collection']

        if raid_id is not None:
            filt = {'tag': 'META', 'zone_id': raid_id}
        else:
            filt = {'tag': 'META', 'raid_name': raid_name}

        raids = list(col.find(filt))
        print(f"Found {len(raids)} raids")

        attendances = {}
        for raid in raids:
            log_id = raid['log_id']
            if player_name is None:
                filt = {'tag': 'PLAYER', 'log_id': log_id}
            else:
                filt = {'tag': 'PLAYER', 'log_id': log_id, 'name': player_name}
            raiders = col.find(filt)
            for raider in raiders:
                if raider['name'] not in attendances:
                    attendances[raider['name']] = AttendanceData(player_name=raider['name'], raid_id=raid_id,
                                                                 raid_name=raid['raid_name'])
                att = attendances[raider['name']]
                att.present_total += 1
                if raider['benched']:
                    att.present_benched += 1
                else:
                    att.present_active += 1

        return len(raids), attendances


if __name__ == "__main__":
    db = Database()
    print("Testing db methods")

    print("getIndex")

    for item in db.getIndex():
        print(item)
