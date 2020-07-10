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
		pass

	def updateDB(self):
		"""
		Update players in database from r.io and wcl
		"""
		pass


if __name__ == "__main__":
	back = Backend()
	print("Testing backend..")
	print("getView")
	for item in back.getView():
		print(item["name"])

