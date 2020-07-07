class Backend:

	def getView(self):
		"""
		Get data to displays
		"""
		
		#placeholder
		return [[1,"Surlo","Warlock","DPS",600,15,2000],[2,"Supsu","Death Knight","DPS", 400,12,1500]]
		

	def getLogs(self):
		"""
		Get most recent logs for guild from WCL
		"""

		#placeholder
		return [["Title1", "date", "http://warcraftlogs.com"], ["title2", "date2", "url2"]]

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


