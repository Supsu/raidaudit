import requests
from dotenv import load_dotenv
import os

class WCLG:

    def __init__(self):
        load_dotenv()
        self.region = os.getenv("WOWREGION")
        self.realm = os.getenv("WOWREALM")
        self.guild = os.getenv("WOWGUILD")
        self.api_id = os.getenv("WCL2ID")
        self.api_secret = os.getenv("WCL2SECRET")
        self.clientapi = "https://www.warcraftlogs.com/"

    def getToken(self):
        tokenurl = self.clientapi + "oauth/token"
        r = requests.post(tokenurl, auth=(self.api_id, self.api_secret), data={
            "grant_type": "client_credentials"
            })

        self.token = r.json()["access_token"]
        #print(self.token)

    def getGuildTags(self):

        self.getToken()

        querystring = f"""
            {{
                guildData {{
                    guild ( name: "{self.guild}", serverRegion: "{self.region}", serverSlug: "{self.realm}" ) {{
                        tags {{
                            id
                            name
                        }}
                    }}
                }}
            }}
        """

        headers = {"Authorization": "Bearer {0}".format(self.token)}

        r = requests.post(self.clientapi + "api/v2/client", json = {'query': querystring}, headers=headers)
        
        tags = r.json()["data"]["guildData"]["guild"]["tags"]

        return tags


    def getAttendance(self, tag=None):

        self.getToken()

        tagstring = ""
        if tag is not None:
            tagstring = " ,guildTagId: {0}".format(tag)

        querystring = f"""
            {{
                guildData {{
                    guild ( name: "{self.guild}", serverRegion: "{self.region}", serverSlug: "{self.realm}" ) {{
                        attendance (limit: 25{tagstring}) {{
                            data  {{
                                code
                                players {{
                                    name
                                    type
                                    presence
                                }}
                                startTime
                                zone {{
                                    id
                                    name
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        """

        #print(querystring)

        headers = {"Authorization": "Bearer {0}".format(self.token)}

        r = requests.post(self.clientapi + "api/v2/client", json = {'query': querystring}, headers=headers)

        #print(r)
        #print(r.json())

        if "error" in r.json():
            return []

        return r.json()["data"]["guildData"]["guild"]["attendance"]["data"]

if __name__ == "__main__":
    w = WCLG()
    print(w.getAttendance())
    print(w.getGuildTags())