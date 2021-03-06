from stat_gatherer import StatGatherer

class GameStats():
    def __init__(self):
        self.stat = StatGatherer()
        self.stat.connect_to_db()


    def get_stats_for_email(self, email):
        player_id = self.stat.find_player_id(player_email=email)
        return self.format_stats_for_player_id(player_id)


    def format_stats_for_player_id(self, player_id):
        player_stats = []
        games_played = self.stat.db.games.find({"players": {"$in": [player_id]}, "winners": { "$exists": True, "$ne": [] } })
        player_stats.append({'description':'Games played', 'value':str(games_played.count())})
        games_won = self.stat.db.games.find({"winners": {"$in": [player_id]}})
        player_stats.append({'description':"Games won", "value":str(games_won.count())})
        player_stats.append({'description':"Games lost", "value":str(games_played.count() - games_won.count())})

        return player_stats

    def print_stats_for_player_id(self, player_id, player_name):
        player_stats = self.format_stats_for_player_id(player_id)
        StatGatherer.print_stats(player_stats, player_name)


def main():

    game_stat = GameStats()

    for player in game_stat.stat.find_all_players():
        player_name = player['email'] if "email" in player else player['username']
        game_stat.print_stats_for_player_id(player['_id'], player_name)


if __name__ == '__main__':
    main()
