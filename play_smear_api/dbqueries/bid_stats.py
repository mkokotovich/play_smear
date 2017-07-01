from stat_gatherer import StatGatherer

class BidStats():
    def __init__(self):
        self.stat = StatGatherer()
        self.stat.connect_to_db()


    def get_stats_for_email(self, email):
        player_id = self.stat.find_player_id(player_email=email)
        return self.format_stats_for_player_id(player_id)


    def format_stats_for_player_id(self, player_id):
        player_stats = {}
        total_bids = self.stat.db.bids.find({'player': player_id, "$where": "this.bid != 0"})
        player_stats['total_bids'] = total_bids.count()
        high_bids = self.stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid"})
        player_stats['high_bids'] = high_bids.count()
        bids_won = self.stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid && this.points_won >= this.bid"})
        player_stats['bids_won'] = bids_won.count()
        player_stats['bids_set'] = player_stats['high_bids'] - player_stats['bids_won']
        total_points_won = 0
        total_points_lost = 0
        for bid in high_bids:
            total_points_won += bid['points_won'] or 0
            total_points_lost += bid['points_lost'] or 0
        player_stats['average_points_won'] = float(total_points_won)/float(player_stats['high_bids']) if player_stats['high_bids'] else 0
        player_stats['average_points_lost'] = float(total_points_lost)/float(player_stats['high_bids']) if player_stats['high_bids'] else 0
        games_played = list(self.stat.db.games.find({"players": {"$in": [player_id]}, "winners": { "$exists": True, "$ne": [] } }))
        hand_count = 0
        for game in games_played:
            hand_count += len(game['hands'])
        player_stats['hands_played'] = hand_count
        player_stats['average_points_per_hand_from_bidding'] = float(total_points_won)/float(player_stats['hands_played']) if player_stats['hands_played'] else 0
        return player_stats


    def print_stats_for_player_id(self, player_id, player_name):
        player_stats = self.format_stats_for_player_id(player_id)
        print ""
        print "{} bid {} times, and was the high bid {} of those times.".format(player_name, player_stats['total_bids'], player_stats['high_bids'])
        print "{} won {} of those bids, and was set {} times ({}% successful).".format(player_name, player_stats['bids_won'], player_stats['bids_set'], 100*float(player_stats['bids_won'])/float(player_stats['high_bids']) if player_stats['high_bids'] else 0)
        print "The average points won during a bid was {}, and the average points lost was {}".format(player_stats['average_points_won'], player_stats['average_points_lost'])
        print "{} played {} hands, and on average won {} points per hand from bidding".format(player_name, player_stats['hands_played'], player_stats['average_points_per_hand_from_bidding'])


def main():

    bid_stat = BidStats()

    for player in bid_stat.stat.find_all_players():
        player_name = player['email'] if "email" in player else player['username']
        bid_stat.print_stats_for_player_id(player['_id'], player_name)


if __name__ == '__main__':
    main()
