import pymongo
from dotenv import load_dotenv
import os
import time

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

        self.client = pymongo.MongoClient(self.dburl, self.dbport, username=self.usr, password=self.pwd, connect=False)
        self.db = self.client.raidaudit

        print("Initialized connection to database " + self.db.name)


    def getIndex(self):
        data = []
        #self.db.players.find() + self.db.autoplayers.find()
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

    def postBlog(self, title, content):
        self.db.blog.insert_one({ "title": title, "content": content, "timestamp": time.strftime('%Y-%m-%d', time.localtime()), "id": int(time.time())})
        #TODO error checking
        return True

    def addPlayer(self, name, charclass, role, automated=False):
        if automated:
            self.db.autoplayers.insert_one( {"name": name, "Class": charclass, "Role": role, "ilv": 0.0, "Weekly": 0, "rio": 0.0, "wcln": 0.0, "wclh": 0.0, "wclm": 0.0} )
        else:
            self.db.players.insert_one( {"name": name, "Class": charclass, "Role": role, "ilv": 0.0, "Weekly": 0, "rio": 0.0, "wcln": 0.0, "wclh": 0.0, "wclm": 0.0} )


    def getManualPlayers(self):
        return self.db.players.find()


    def updateRole(self, playername, newrole, automated):
        if automated:
            self.db.autoplayers.update_one({"name": playername}, {"$set": {"Role": newrole}})
        else:
            self.db.players.update_one({"name": playername}, {"$set": {"Role": newrole}})

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


if __name__ == "__main__":
    db = Database()
    print("Testing db methods")

    print("getIndex")

    for item in db.getIndex():
        print(item)

          
