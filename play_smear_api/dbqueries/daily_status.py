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

    
    def find_winning_score(self, game):
        for result in game["results"]:
            if result["player"] in game["winners"]:
                return result["final_score"]
    

    def find_losing_scores(self, game):
        losing_scores = []
        losing_teams = []
        for result in game["results"]:
            if result["player"] not in game["winners"] and result["team_id"] not in losing_teams:
                losing_scores.append(result["final_score"])
                losing_teams.append(result["team_id"])
        return losing_scores


    def get_num_games(self):
        return len(self.game_list)


    def print_game_stats(self):
        message = ""
        message += "\n"
        message += "There have been {} games played since {}:".format(len(self.game_list), self.local_time)
        message += "\n"
        message += "\n"
        for game in self.game_list:
            message += "  Game {}:".format(game["_id"])
            message += "\n"
            message += "    Players: {}".format(", ".join(self.find_player_names_from_ids(game["players"])))
            message += "\n"
            message += "    Number of hands played: {}".format(len(game["hands"]))
            message += "\n"
            if game["winners"]:
                message += "    Final score: {} - {}".format(self.find_winning_score(game), ", ".join(str(x) for x in self.find_losing_scores(game)))
                message += "\n"
                message += "    Winners: {}".format(", ".join(self.find_player_names_from_ids(game["winners"])))
                message += "\n"
            message += "\n"
        return message


def main():

    number_of_days = 1
    if len(sys.argv) > 1:
        try:
            number_of_days = int(sys.argv[1])
        except ValueError:
            print "Invalide number of days: " + sys.argv[1]
    daily_status = DailyStatus()
    daily_status.load_stats_since_previous_date(number_of_days)
    print daily_status.print_game_stats()


if __name__ == '__main__':
    main()
