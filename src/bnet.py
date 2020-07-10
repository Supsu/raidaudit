import time
import requests
from dotenv import load_dotenv
import os
import json

class Bnet:
	_id = ""
	_secret = ""
	_token = ""
	_expires = 0
	_timestamp = 0
	_region = ""
	_guild = ""
	_realm = ""
	_apiurl = ""
	_namespace = ""
	_locale = ""

	def __init__(self):
		self._timestamp = time.time()

		load_dotenv()

		self._region = os.getenv("WOWREGION")
		self._guild = os.getenv("WOWGUILD")
		self._realm = os.getenv("WOWREALM")
		self._id = os.getenv("BNETID")
		self._secret = os.getenv("BNETSECRET")
		self._namespace = os.getenv("WOWNAMESPACE")
		self._locale = os.getenv("WOWLOCALE")
		self._apiurl = "https://" + self._region + ".api.blizzard.com/"

		print("BNETID " + self._id )
		print("BNETSECRET " + self._secret )

	def getAccessToken(self):
		"""
		Get access token with given id and secret
		"""
		print("Checking access token..")
		
		
		checkurl = "https://" + self._region + ".battle.net/oauth/check_token"
		r = requests.post(checkurl, data={"token":self._token})

		#if "error" not in r:
		#	return self._token
		
		print("Getting new access token for battle.net API")
		# get new token
		tokenurl = "https://"+ self._region +".battle.net/oauth/token"
		r = requests.post(tokenurl, auth=(self._id, self._secret), data={"grant_type":"client_credentials"})
		print(str(r.status_code))
		if str(r.status_code) != str(200):
			print("ERROR " + str(r.status_code))
			print("R: " + r)
			return "ERROR " + str(r.status_code)
		data = r.json()
		self._token = data["access_token"]
		self._expires = int(data["expires_in"])
		return self._token

	
	
	def getRoster(self):
		"""
		Gets guild roster from b.net API to automatically add raiders
		"""
		print("Getting roster..")
		self._token = self.getAccessToken()
		reqUrl = self._apiurl + "data/wow/guild/" + self._realm + "/" + self._guild + "/roster?namespace=" + self._namespace + "&locale=" + self._locale + "&access_token=" + self._token
		
		req = requests.get(reqUrl)
		print(str(req.status_code))
		#reqjson = req.json()

		return req


	def getCharacterProfile(self, charname, realm=None):
		"""
		get profile for a certain character
		"""
		
		if realm == None:
			realm = self._realm

		print("Getting character profile for " + charname + " from " + realm)

		atoken = self.getAccessToken()
		reqUrl = self._apiurl + "data/wow/character/" + realm + "/" + charname + "?namespace=" + self._namespace + "&locale=" + self._locale + "&access_token=" + self._token
		

		req = requests.get(reqUrl)
		reqjson = req.json()

		return reqjson


	


if __name__ == "__main__":
	print("Running as main, testing..")
	bnet = Bnet()
	print(bnet.getRoster())
	print(bnet.getCharacterProfile("surlo"))