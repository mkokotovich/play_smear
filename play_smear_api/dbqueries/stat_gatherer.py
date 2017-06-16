from pymongo import MongoClient
import os


class StatGatherer():
    def __init__(self):
        self.db = None


    def connect_to_db(self, default_host="localhost", default_port="27017", default_db="smear"):
        # Connect to database
        if "MONGODB_URI" in os.environ:
            mongo_uri = os.environ["MONGODB_URI"]
            database = mongo_uri.split('/')[-1]
            client = MongoClient(mongo_uri)
            self.db = client[database]
        else:
            client = MongoClient("{}:{}".format(default_host, default_port))
            self.db = client[default_db]

    
    def find_player_id(self, player_email=None, player_username=None):
        player = None
        player_id = None
        if player_email is None and player_username is None:
            return player
        if player_email:
            player = self.db.players.find_one({"email": player_email})
        else:
            player = self.db.players.find_one({"username": player_username})
        if player:
            player_id = player["_id"]
        return player_id


