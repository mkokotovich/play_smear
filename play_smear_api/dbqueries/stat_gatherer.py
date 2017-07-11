from pymongo import MongoClient
import os


class StatGatherer(object):
    def __init__(self):
        self.db = None


    def connect_to_db(self, default_host="localhost", default_port="27017", default_db="smear"):
        # Connect to database
        database = None
        uri = None
        if "MONGODB_URI" in os.environ:
            uri = os.environ["MONGODB_URI"]
            database = uri.split('/')[-1]
        else:
            uri = "{}:{}".format(default_host, default_port)
            database = default_db
        print "Connecting to {} on {}".format(database, uri)
        client = MongoClient(uri)
        self.db = client[database]

    
    def find_all_players(self):
        players = self.db.players.find()
        return list(players)

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


    @staticmethod
    def add_stat_to_list(stat_list, description, value):
        stat_list.append({"description": description, "value": str(value)})


    @staticmethod
    def print_stats(player_stats, player_name):
        print ""
        print "Stats for " + player_name + ":"
        for stat in player_stats:
            print stat['description'] + ": " + stat['value']

