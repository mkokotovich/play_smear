from functools import wraps
from datetime import datetime

from pymongo import MongoClient
import pytz

def swallow_exceptions(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            print "Exception occurred while trying to use database: {}".format(str(ex))
    return func_wrapper

class DbManager():

    def __init__(self, database="smear", hostname="localhost", port=27017, client=None, debug=False):
        if client == None:
            self.client = MongoClient("{}:{}".format(hostname, port))
        else:
            self.client = client
        self.debug = debug
        self.db = self.client[database]
        self.current_game_record = self.init_game_record()
        self.current_hand_record = self.init_game_record()
        self.current_bid_record = None
        self.player_map = {}
        self.game_id = None
        self.connection_errors = False


    @swallow_exceptions
    def init_game_record(self):
        game_record = {}
        game_record['date_added'] = None
        game_record['points_to_play_to'] = None
        game_record['num_teams'] = None
        game_record['players'] = []
        game_record['hands'] = []
        game_record['winners'] = []
        game_record['results'] = []
        return game_record


    @swallow_exceptions
    def init_hand_record(self):
        hand_record = {}
        hand_record['date_added'] = None
        hand_record['bids'] = []
        hand_record['high_bid'] = None
        hand_record['players'] = []
        hand_record['dealer_forced_two_set'] = None
        return hand_record


    @swallow_exceptions
    def init_bid_record(self):
        bid_record = {}
        bid_record['date_added'] = None
        bid_record['game'] = None
        bid_record['player'] = None
        bid_record['bidders_hand'] = []
        bid_record['bid_so_far'] = None
        bid_record['bid'] = None
        bid_record['bid_trump'] = None
        bid_record['high_bid'] = None
        bid_record['num_teams'] = 0
        bid_record['num_players'] = 0
        bid_record['points_won'] = None
        bid_record['points_lost'] = None
        return bid_record


    @swallow_exceptions
    def create_game(self, points_to_play_to, num_teams):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        self.game_id = None
        # For some reason this needs to persist between games for the simulator
        if "players" in self.current_game_record and len(self.current_game_record['players']) > 0:
            save_players = self.current_game_record['players']
            self.current_game_record = self.init_game_record()
            self.current_game_record['players'] = save_players
        self.current_game_record['points_to_play_to'] = points_to_play_to
        self.current_game_record['num_teams'] = num_teams


    @swallow_exceptions
    def lookup_or_create_player(self, username, email):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return None
        player_found_by_email = False
        player_id = None
        try:
            if email:
                find_result = self.db.players.find({'email': email})
                if find_result.count() != 0:
                    player_found_by_email = True
                    if self.debug:
                        print "DB: Found {} by email: {}".format(username, email)
                    if 'username' not in find_result[0] or find_result[0]['username'] != username:
                        if self.debug:
                            print "DB: Updating username to {}".format(username)
                        player_record = dict(find_result[0])
                        player_record['username'] = username
                        self.db.players.update({'_id':player_record['_id']}, player_record)

            if not player_found_by_email:
                if self.debug:
                    print "DB: Could not find {} by email".format(username)
                find_result = self.db.players.find({'username': username})
            if find_result.count() != 0:
                player_id = find_result[0]['_id']
                if self.debug:
                    print "DB: Found existing user: {}".format(player_id)
            else:
                player_record = {}
                player_record["username"] = username
                if email:
                    player_record["email"] = email
                if self.debug:
                    print "DB: Could not find {}, inserting into player database".format(username)
                insert_result = self.db.players.insert_one(player_record)
                if not insert_result.acknowledged:
                    print "DB: Error: unable to create user {} in database".format(username)
                    return None
                player_id = insert_result.inserted_id
        except Exception as ex:
            print "DB: exception reached: {}".format(str(ex))
            self.connection_errors = True
        return player_id


    @swallow_exceptions
    def add_player(self, username, email=None):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        player_id = self.lookup_or_create_player(username, email)
        self.current_game_record['players'].append(player_id)
        self.player_map[username] = player_id


    @swallow_exceptions
    def add_game_to_db_for_first_time(self):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        self.current_game_record['date_added'] = datetime.utcnow()
        insert_result = self.db.games.insert_one(self.current_game_record)
        if not insert_result.acknowledged:
            print "DB: Error: unable to create game in database"
            return
        self.game_id = insert_result.inserted_id
        if self.debug:
            print "DB: Adding game {} to database".format(self.game_id)


    @swallow_exceptions
    def add_new_bid(self, username, bidders_hand, bid, high_bid, is_high_bid):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        # Create bid record
        new_bid = self.init_bid_record()
        new_bid['date_added'] = datetime.utcnow()
        new_bid['game'] = self.game_id
        new_bid['player'] = self.player_map[username]
        new_bid['bidders_hand'] = bidders_hand
        new_bid['bid_so_far'] = None #TODO
        new_bid['bid'] = bid
        new_bid['high_bid'] = high_bid
        new_bid['num_teams'] = self.current_game_record['num_teams']
        new_bid['num_players'] = len(self.current_game_record['players'])
        # Will be added after hand is completed
        new_bid['bid_trump'] = None
        new_bid['points_won'] = None
        new_bid['points_lost'] = None

        # Add bid to database
        insert_result = self.db.bids.insert_one(new_bid)
        if not insert_result.acknowledged:
            print "DB: Error: unable to create bid of {} for {} in database".format(bid, username)
            return
        if self.debug:
            print "DB: Adding bid of {} from {} (id: {}) to database".format(bid, username, insert_result.inserted_id)

        # Add bid to hand
        self.current_hand_record['bids'].append(insert_result.inserted_id)
        if is_high_bid:
            self.current_bid_record = new_bid
            self.current_hand_record['high_bid'] = insert_result.inserted_id


    @swallow_exceptions
    def create_new_hand(self):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        self.current_hand_record = self.init_hand_record()
        self.current_hand_record['date_added'] = datetime.utcnow()
        self.current_hand_record['players'] = list(self.current_game_record['players'])


    @swallow_exceptions
    def finalize_hand_creation(self, dealer_forced_two_set):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        if dealer_forced_two_set:
            self.current_hand_record['dealer_forced_two_set'] = self.player_map[dealer_forced_two_set]
        # Add hand to database
        insert_result = self.db.hands.insert_one(self.current_hand_record)
        if not insert_result.acknowledged:
            print "DB: Error: unable to create bid of {} for {} in database".format(bid, username)
            return
        self.current_game_record['hands'].append(insert_result.inserted_id)
        if self.debug:
            print "DB: Adding hand {} to database".format(insert_result.inserted_id)


    @swallow_exceptions
    def convert_usernames_to_object_ids(self, results):
        for player_result in results:
            player_id = self.player_map[player_result["player"]]
            player_result["player"] = player_id
        return results


    @swallow_exceptions
    def publish_hand_results(self, trump, points_won, points_lost, results, overall_winners):
        if self.connection_errors:
            print "DB: skipping due to connection errors"
            return
        if overall_winners:
            # Game is over
            if self.debug:
                print "DB: Game is over, adding winners and results to game"
            self.current_game_record["winners"] = [ self.player_map[x] for x in overall_winners ]
            self.current_game_record["results"] = self.convert_usernames_to_object_ids(results)
        if self.current_bid_record is None:
            # I think this might happen if the dealer passes? Not sure, seeing it in tests
            return
        self.current_bid_record["bid_trump"] = trump
        self.current_bid_record["points_won"] = points_won
        self.current_bid_record["points_lost"] = points_lost
        bid_update = self.db.bids.replace_one({'_id':self.current_bid_record['_id']}, self.current_bid_record)
        if not bid_update.acknowledged:
            print "DB: Error: unable to update bid"
        game_update = self.db.games.replace_one({'_id':self.current_game_record['_id']}, self.current_game_record)
        if not game_update.acknowledged:
            print "DB: Error: unable to update game"
        if self.debug:
            print "DB: Updated bid and game"
