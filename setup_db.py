import pymongo
import urllib.parse

print("Welcome to MongoDB setup wizard for raidaudit")
print("You can also set your database up yourself via mongo CLI")
print("For now this only sets admin login to admin / passw0rd")
print("-----")

url = input("Address of your MongoDB instance? (without port) > ")
port = input("Port of your MongoDB instance? > ")
auth = ""

while (auth is not "Y" and auth is not "y" and auth is not "N" and auth is not "n"):
    auth = input("Does your MongoDB instance require authentication? > ")
conn = ""

if auth == "Y":
    login = urllib.parse.quote_plus(input("Please provide login name for MongoDB > "))
    pwd = urllib.parse.quote_plus(input("Please provide password > "))
    conn = "mongodb://{}:{}@".format(login, pwd) + url

else:
    conn = "mongodb://" + url


client = pymongo.MongoClient(conn, int(port))

db = client.raidaudit

db.settings.insert_one( { 
    "updated": "never",
    "adminname": "admin",
    "adminpwd": "passw0rd"
 } )