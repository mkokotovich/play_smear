from stat_gatherer import StatGatherer
from datetime import datetime, timedelta
from dateutil import tz
import sys

class DailyStatus():
    def __init__(self):
        self.stat = StatGatherer()
        self.stat.connect_to_db()
        self.game_list = None
        self.bid_list = None
        self.player_list = None
        self.local_time = None


    def load_stats_since_previous_date(self, number_of_days):
        # Assume we are running some time after 4am CDT (which is 9am UTC)
        # "Yesterday" should go form 9am UTC on previous day to 9am UTC today
        yesterday_start = datetime.utcnow() - timedelta(days=number_of_days)
        yesterday_start = yesterday_start.replace(hour = 9, minute = 0, second = 0, microsecond = 0)

        # Save the start time in local time zone
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        yesterday_with_tz = yesterday_start.replace(tzinfo=from_zone)
        self.local_time = yesterday_with_tz.astimezone(to_zone)

        self.game_list = list(self.stat.db.games.find({"date_added" : { "$gte" : yesterday_start }}))
        self.bid_list = list(self.stat.db.bids.find({"date_added" : { "$gte" : yesterday_start }}))
        self.player_list = list(self.stat.db.players.find())


    def find_player_names_from_ids(self, player_ids):
        player_names = []
        for player_id in player_ids:
            player_names.append(next((x["username"] for x in self.player_list if x["_id"] == player_id), "Unknown"))
        return player_names

    
    def print_game_stats(self):
        print "There have been {} games played since {}:".format(len(self.game_list), self.local_time)
        for game in self.game_list:
            print "  Game {}:".format(game["_id"])
            print "    Players: {}".format(", ".join(self.find_player_names_from_ids(game["players"])))
            print "    Number of hands played: {}".format(len(game["hands"]))
            if game["winners"]:
                print "    Winners: {}".format(", ".join(self.find_player_names_from_ids(game["winners"])))


def main():

    number_of_days = 1
    if len(sys.argv) > 1:
        try:
            number_of_days = int(sys.argv[1])
        except ValueError:
            print "Invalide number of days: " + sys.argv[1]
    daily_status = DailyStatus()
    daily_status.load_stats_since_previous_date(number_of_days)
    daily_status.print_game_stats()



if __name__ == '__main__':
    main()
