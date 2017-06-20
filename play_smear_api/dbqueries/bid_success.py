from stat_gatherer import StatGatherer
import operator

class BidSuccess():
    def __init__(self, debug=False):
        self.debug = debug
        self.stat = StatGatherer()
        self.stat.connect_to_db()
        self.high_bids = None
        self.players = None
        self.with_ace_percentage = 0
        self.without_ace_percentage = 0
        self.player_success = {}


    def did_bid_have_ace_of_trump(self, bid):
        ace = "A" + bid["bid_trump"][0]
        return ace in bid["bidders_hand"]


    def find_success_of_ace_or_not(self):
        with_ace_made = 0
        with_ace_set = 0
        with_ace_total = 0

        without_ace_made = 0
        without_ace_set = 0
        without_ace_total = 0

        if self.high_bids == None:
            self.high_bids = list(self.stat.db.bids.find({"$where": "this.bid == this.high_bid"}))

        for bid in self.high_bids:
            if "bid_trump" not in bid:
                continue
            if self.did_bid_have_ace_of_trump(bid):
                with_ace_total += 1
                if self.debug:
                    print "bid of {} made {} with the ace".format(bid["bid"], bid["points_won"])
                if bid["points_won"] >= bid["bid"]:
                    with_ace_made += 1
                else:
                    with_ace_set += 1
            else:
                without_ace_total += 1
                if self.debug:
                    print "bid of {} made {} without the ace".format(bid["bid"], bid["points_won"])
                if bid["points_won"] >= bid["bid"]:
                    without_ace_made += 1
                else:
                    without_ace_set += 1

        self.with_ace_percentage = 100 * float(with_ace_made) / float(with_ace_total)
        self.without_ace_percentage = 100 * float(without_ace_made) / float(without_ace_total)


    def find_success_by_player(self):
        if self.high_bids == None:
            self.high_bids = list(self.stat.db.bids.find({"$where": "this.bid == this.high_bid"}))

        if self.players == None:
            self.players = list(self.stat.db.players.find())

        for player in self.players:
            player_id = player["_id"]
            player_high_bids = [ x for x in self.high_bids if x["player"] == player_id ]
            player_bids_won = [ x for x in player_high_bids if x["points_won"] >= x["bid"] ]
            if len(player_high_bids) > 0:
                self.player_success[player["username"]] = 100 * float(len(player_bids_won)) / float(len(player_high_bids))

        

def main():

    bid_success = BidSuccess()
    bid_success.find_success_of_ace_or_not()

    print "Bids with the Ace of trump are {}% successful".format(bid_success.with_ace_percentage)
    print "Bids without the Ace of trump are {}% successful".format(bid_success.without_ace_percentage)

    bid_success.find_success_by_player()
    sorted_success = sorted(bid_success.player_success.items(), key=operator.itemgetter(1), reverse=True)
    print "Players ranked by their bid success rate:"
    for player, success in sorted_success:
        print "{}: {}%".format(player, success)


if __name__ == '__main__':
    main()
