from typing import Dict, List

import pymongo
from dotenv import load_dotenv
import os
import time
from dataclasses import asdict
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


if __name__ == "__main__":
    db = Database()
    print("Testing db methods")

    print("getIndex")

    for item in db.getIndex():
        print(item)
