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
	raiderrank = 0

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

		listed = sorted(data, key=sorter)

		return listed
		
	def getBlog(self):
		"""
		Get blog posts
		"""
		data = self.db.getBlog()
		return data

	def getSingleBlog(self, id):
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
			row["start"] = time.strftime('%Y-%m-%d', time.localtime(int(row["start"]/1000)))

		return data

	def updateView(self):
		"""
		Update view tables from db
		"""
		pass

	def addPlayer(self, player):
		"""
		Add player to roster manually
		"""

		self.db.addPlayer(player["name"],player["Class"],player["Role"])

		return True
		

	def removePlayer(self, player):
		"""
		Remove player from roster
		"""
		pass

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
			tmp = { "name": "",
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

			print("Getting ilv from battle.net profile for " + name)
			bnetprofile = self.bnet.getCharacterProfile(name)
			tmp["ilv"] = bnetprofile["average_item_level"]

			print("Getting m+ data from raider.io for " + name)
			rioprofile = self.rio.getProfile(name)

			# will return empty list if there are no runs for the week
			if len(rioprofile["mythic_plus_weekly_highest_level_runs"]) == 0:
				tmp["Weekly"] = 0
			else:
				tmp["Weekly"] = int(rioprofile["mythic_plus_weekly_highest_level_runs"][0]["mythic_level"])

			# in case of no data, should still return 0 as a score
			tmp["rio"] = float( rioprofile["mythic_plus_scores_by_season"][0]["scores"]["all"] )


			wclperf = self.wcl.getPlayerAvg(name)

			tmp["wcln"] = wclperf["avgN"]
			tmp["wclh"] = wclperf["avgH"]
			tmp["wclm"] = wclperf["avgM"]

			dbquery = {"name": name}
			dbnewdata = { "$set": tmp }
			
			# push updated automated players to DB
			# TODO create a method for updating in db.py this is ugly
			self.db.db.autoplayers.update_one(dbquery, dbnewdata, upsert=True)
		

		# TODO refactor this to have only one loop / function call
		# ugly repeating loop

		for i in manuals:
			tmp = { "name": "",
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

			print("Getting ilv from battle.net profile for " + name)
			bnetprofile = self.bnet.getCharacterProfile(name)
			tmp["ilv"] = bnetprofile["average_item_level"]

			print("Getting m+ data from raider.io for " + name)
			rioprofile = self.rio.getProfile(name)
			# will return empty list if there are no runs for the week
			if len(rioprofile["mythic_plus_weekly_highest_level_runs"]) == 0:
				tmp["Weekly"] = 0
			else:
				tmp["Weekly"] = int(rioprofile["mythic_plus_weekly_highest_level_runs"][0]["mythic_level"])
			
			tmp["rio"] = float( rioprofile["mythic_plus_scores_by_season"][0]["scores"]["all"] )


			wclperf = self.wcl.getPlayerAvg(name)

			tmp["wcln"] = wclperf["avgN"]
			tmp["wclh"] = wclperf["avgH"]
			tmp["wclm"] = wclperf["avgM"]

			dbquery = {"name": name}
			dbnewdata =  { "$set": tmp }
			
			# push updated automated players to DB
			# TODO create a method for updating in db.py this is ugly
			self.db.db.players.update_one(dbquery, dbnewdata, upsert=True)


		#Update updating time to settings
		#TODO this needs methods, ugly
		print("Setting update timestamp to " + str(int(time.time())) )
		response = self.db.db.settings.update_one({}, {"$set": {"timestamp": int(time.time()) }}, upsert=False)
		print("Modified " + str(response.modified_count) + " entries")

		# TODO implement some kind of error handling and return False in
		# case there is an error
		return True


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

	def getUpdateTimestamp(self):
		return self.db.getSettings()["timestamp"]


	def editPlayerRole(self, playername, playerrole, automated):
		self.db.updateRole(playername, playerrole, automated)

if __name__ == "__main__":
	back = Backend()
	print(back.getUpdateTimestamp())
	
	

