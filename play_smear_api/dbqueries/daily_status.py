from stat_gatherer import StatGatherer
from datetime import datetime, timedelta

class DailyStatus():
    def __init__(self):
        self.stat = StatGatherer()
        self.stat.connect_to_db()
        self.game_list = None
        self.bid_list = None
        self.player_list = None


    def load_stats_since_yesterday(self):
        # Assume we are running some time after 4am CDT (which is 9am UTC)
        # "Yesterday" should go form 9am UTC on previous day to 9am UTC today
        yesterday_start = datetime.utcnow() - timedelta(days=1)
        yesterday_start = yesterday_start.replace(hour = 9, minute = 0, second = 0, microsecond = 0)
        self.game_list = list(self.stat.db.games.find({"date_added" : { "$gte" : yesterday_start }}))
        self.bid_list = list(self.stat.db.bids.find({"date_added" : { "$gte" : yesterday_start }}))
        self.player_list = list(self.stat.db.players.find())


    def find_player_names_from_ids(self, player_ids):
        player_names = []
        for player_id in player_ids:
            player_names.append(next((x["username"] for x in self.player_list if x["_id"] == player_id), "Unknown"))
        return player_names

    
    def print_game_stats(self):
        print "There have been {} games played since yesterday:".format(len(self.game_list))
        for game in self.game_list:
            print "  Game {}:".format(game["_id"])
            print "    Players: {}".format(", ".join(self.find_player_names_from_ids(game["players"])))
            print "    Number of hands played: {}".format(len(game["hands"]))
            if game["winners"]:
                print "    Winners: {}".format(", ".join(self.find_player_names_from_ids(game["winners"])))


def main():

    daily_status = DailyStatus()
    daily_status.load_stats_since_yesterday()
    daily_status.print_game_stats()



if __name__ == '__main__':
    main()
