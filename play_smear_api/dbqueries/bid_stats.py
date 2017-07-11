from stat_gatherer import StatGatherer

class BidStats():
    def __init__(self):
        self.stat = StatGatherer()
        self.stat.connect_to_db()


    def get_stats_for_email(self, email):
        player_id = self.stat.find_player_id(player_email=email)
        return self.format_stats_for_player_id(player_id)


    def format_stats_for_player_id(self, player_id):
        player_stats = []
        total_bids = self.stat.db.bids.find({'player': player_id, "$where": "this.bid != 0"})
        StatGatherer.add_stat_to_list(player_stats, "Total number of bids", total_bids.count())
        high_bids = self.stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid"})
        StatGatherer.add_stat_to_list(player_stats, "How many of those bids were the high bid", high_bids.count())
        bids_won = self.stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid && this.points_won >= this.bid"})
        StatGatherer.add_stat_to_list(player_stats, "Bids won", bids_won.count())
        StatGatherer.add_stat_to_list(player_stats, "Bids set", high_bids.count() - bids_won.count())
        total_points_won = 0
        total_points_lost = 0
        for bid in high_bids:
            total_points_won += bid['points_won'] or 0
            total_points_lost += bid['points_lost'] or 0
        StatGatherer.add_stat_to_list(player_stats, 'Average number of points won while bidding', float(total_points_won)/float(high_bids.count()) if high_bids.count() else 0)
        StatGatherer.add_stat_to_list(player_stats, 'Average number of points lost while bidding', float(total_points_lost)/float(high_bids.count()) if high_bids.count() else 0)

        games_started = list(self.stat.db.games.find({"players": {"$in": [player_id]}}))
        hand_count = 0
        for game in games_started:
            hand_count += len(game['hands'])
        StatGatherer.add_stat_to_list(player_stats, "Number of hands played", hand_count)
        StatGatherer.add_stat_to_list(player_stats, "Average points per hand won from bidding",float(total_points_won)/float(hand_count) if hand_count else 0)

        return player_stats


    def print_stats_for_player_id(self, player_id, player_name):
        player_stats = self.format_stats_for_player_id(player_id)
        StatGatherer.print_stats(player_stats, player_name)


def main():

    bid_stat = BidStats()

    for player in bid_stat.stat.find_all_players():
        player_name = player['email'] if "email" in player else player['username']
        bid_stat.print_stats_for_player_id(player['_id'], player_name)


if __name__ == '__main__':
    main()
