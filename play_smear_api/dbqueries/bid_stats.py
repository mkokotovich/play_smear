from stat_gatherer import StatGatherer

def print_stats_for_player_id(stat, player_id, player):
    total_bids = stat.db.bids.find({'player': player_id, "$where": "this.bid != 0"})
    total_bids_count = total_bids.count()
    high_bids = stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid"})
    high_bids_count = high_bids.count()
    bids_won = stat.db.bids.find({'player': player_id, "$where": "this.bid == this.high_bid && this.points_won >= this.bid"})
    bids_won_count = bids_won.count()
    total_points_won = 0
    total_points_lost = 0
    for bid in high_bids:
        total_points_won += bid['points_won'] or 0
        total_points_lost += bid['points_lost'] or 0
    average_points_won = float(total_points_won)/float(high_bids_count) if high_bids_count else 0
    average_points_lost = float(total_points_lost)/float(high_bids_count) if high_bids_count else 0

    print ""
    print "{} bid {} times, and was the high bid {} of those times.".format(player, total_bids_count, high_bids_count)
    print "{} won {} of those bids, and was set {} times.".format(player, bids_won_count, high_bids_count - bids_won_count)
    print "The average points won during a bid was {}, and the average points lost was {}".format(average_points_won, average_points_lost)

def main():

    stat = StatGatherer()
    stat.connect_to_db()

    player_emails= [
        'mkokotovich@gmail.com',
    ]
    player_usernames = [
        'player0',
        'player1',
        'player2',
        'player3',
    ]

    #for email in player_emails:
    #    player_id = stat.find_player_id(player_email=email)
    #    if player_id:
    #        print_stats_for_player_id(stat, player_id, email)
    #for username in player_usernames:
    #    player_id = stat.find_player_id(player_username=username)
    #    if player_id:
    #        print_stats_for_player_id(stat, player_id, username)
    for player in stat.find_all_players():
        player_name = player['email'] if "email" in player else player['username']
        print_stats_for_player_id(stat, player['_id'], player_name)


if __name__ == '__main__':
    main()
