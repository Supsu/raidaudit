from db import Database
from bnet import Bnet
from rio import RIO
from wcl import WCL
import json
import time


class Backend:

	db = ""
	bnet = ""
	rio = ""
	wcl = ""

	def __init__(self):
		self.db = Database()
		self.bnet = Bnet()
		self.rio = RIO()
		self.wcl = WCL()

	def getView(self):
		"""
		Get data for roster table
		"""

		def sorter(item):
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
		listed = []
		for item in data:
			# force weekly to display as int
			item["Weekly"] = int(item["Weekly"])
			listed.append(item)

		listed = sorted(listed, key=sorter)

		return listed
		
	def getBlog(self):
		"""
		Get blog posts
		"""
		data = self.db.getBlog()
		return data


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
			row["start"] = time.strftime('%Y-%m-%d', time.localtime(int(row["start"]/1000)))

		return data

	def updateView(self):
		"""
		Update view tables from db
		"""
		pass

	def addPlayer(self, player):
		"""
		Add player to roster
		"""
		pass

	def removePlayer(self, player):
		"""
		Remove player from roster
		"""
		pass

	def updateRoster(self):
		"""
		Update raider rank characters from armory
		"""

		CLASSID = {
			1: "Warrior",
			2: "Paladin",
			3: "Hunter",
			4: "Rogue",
			5: "Priest",
			6: "Death Knight",
			7: "Shaman",
			8: "Mage",
			9: "Warlock",
			10: "Monk",
			11: "Druid",
			12: "Demon Hunter"
		}

		roster = self.bnet.getRoster()

		for player in roster:
			character = player[0]["character"]

			name = player["character"]["name"]
			print(name)
			rank = player["character"]["rank"]
			print(rank)
			charclass = CLASSID[player["character"]["playable_class"]["id"]]
			print(id)



		pass

	def updateDB(self):
		"""
		Update players in database from r.io and wcl
		"""
		pass

	def login(self, usr, pwd):
		"""
		Check login information
		"""

		settings = self.db.getSettings()

		boolusr=False
		boolpwd=False

		# check admin credentials
		if settings["adminname"] == usr:
			boolusr=True
		if settings["adminpwd"] == pwd:
			boolpwd=True

		if boolusr and boolpwd:
			return boolusr, boolpwd
		else:
			#check additional login table for officers etc
			#TODO
			return boolusr, boolpwd


	def post(self, title, content):
		r = self.db.postBlog(title, content)

		return r

		


if __name__ == "__main__":
	back = Backend()
	back.updateRoster()
	

