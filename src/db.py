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

        self.client = pymongo.MongoClient(self.dburl, self.dbport, username=self.usr, password=self.pwd)
        self.db = self.client.raidaudit

        print("Initialized connection to database " + self.db.name)


    def getIndex(self):
        return self.db.players.find()

    
    def getBlog(self):
        return self.db.blog.find().sort("timestamp", pymongo.DESCENDING)

    def getSettings(self):
        return self.db.settings.find_one()

    def postBlog(self, title, content):
        self.db.blog.insert_one({ "title": title, "content": content, "timestamp": time.strftime('%Y-%m-%d', time.localtime())})
        #TODO error checking
        return True

if __name__ == "__main__":
    db = Database()
    print("Testing db methods")

    print("getIndex")

    for item in db.getIndex():
        print(item)

    print("getBlog")

    for post in db.getBlog():
        print(post)

    print("getSettings")

    print(db.getSettings())
          