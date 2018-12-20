import unittest
import sys
import pytz
from datetime import datetime
import mongomock

sys.path.insert(0, "..")
import pysmear.db_manager

class TestDbManager(unittest.TestCase):
    def setUp(self):
        self.dbm = pysmear.db_manager.DbManager(client=mongomock.MongoClient())
        self.clear_database_and_dbm()

    def clear_database_and_dbm(self):
        self.dbm.db.players.drop()
        self.dbm.current_game_record = self.dbm.init_game_record()

    def create_game_record(self, points_to_play_to=11, num_teams=0):
        game_record = {}
        game_record['date_played'] = datetime.now(pytz.utc)
        game_record['points_to_play_to'] = points_to_play_to
        game_record['num_teams'] = num_teams
        game_record['players'] = []
        game_record['hands'] = []
        game_record['winners'] = []
        game_record['results'] = []
        return game_record

    def assert_user_is_in_users(self, username):
        find_result = self.dbm.db.players.find({'username': username})
        self.assertEqual(find_result.count(), 1)
        return find_result[0]['_id']

    def test_create_game(self):
        self.dbm.create_game(11, 0)
        self.assertEqual(self.dbm.current_game_record['points_to_play_to'], 11)
        self.assertEqual(self.dbm.current_game_record['num_teams'], 0)

    def test_add_player_with_new_player(self):
        self.clear_database_and_dbm()
        self.dbm.add_player("new_player")
        player_id = self.assert_user_is_in_users("new_player")
        dbm_players = self.dbm.current_game_record['players']
        self.assertEqual(len(dbm_players), 1)
        self.assertEqual(dbm_players[0], player_id)
        self.assertEqual(self.dbm.player_map["new_player"], player_id)

    def test_add_player_with_repeat_player(self):
        self.clear_database_and_dbm()
        username = "repeat_player"
        insert_result = self.dbm.db.players.insert_one({'username': username})
        inserted_player_id = insert_result.inserted_id
        self.dbm.add_player(username)
        player_id = self.assert_user_is_in_users(username)
        self.assertEqual(inserted_player_id, player_id)
        dbm_players = self.dbm.current_game_record['players']
        self.assertEqual(len(dbm_players), 1)
        self.assertEqual(dbm_players[0], player_id)
        self.assertEqual(self.dbm.player_map[username], player_id)


    def test_add_game_to_db_for_first_time(self):
        self.clear_database_and_dbm()
        self.dbm.create_game(11, 0)
        self.dbm.add_player("player0")
        self.dbm.add_player("player1")
        self.dbm.add_game_to_db_for_first_time()
        game_id = self.dbm.game_id
        find_result = self.dbm.db.games.find({'_id': game_id})
        self.assertEqual(find_result.count(), 1)


    def test_add_new_bid(self):
        self.clear_database_and_dbm()
        self.dbm.create_game(11, 0)
        self.dbm.add_player("player0")
        self.dbm.add_game_to_db_for_first_time()
        self.dbm.create_new_hand()
        self.dbm.add_new_bid("player0", ["AS", "KS", "QS", "JS", "JC", "2S" ], 4, 4, True)
        find_result = self.dbm.db.bids.find({"player": self.dbm.player_map["player0"]})
        self.assertEqual(find_result.count(), 1)
        self.assertEqual(find_result[0]["bid"], 4)
        self.assertEqual(self.dbm.current_hand_record['high_bid'], find_result[0]['_id'])


    def test_finalize_hand_creation(self):
        self.clear_database_and_dbm()
        self.dbm.create_game(11, 0)
        self.dbm.add_player("player0")
        self.dbm.add_game_to_db_for_first_time()
        self.dbm.create_new_hand()
        self.dbm.add_new_bid("player0", ["AS", "KS", "QS", "JS", "JC", "2S" ], 4, 4, True)
        self.dbm.finalize_hand_creation(False)
        find_result = self.dbm.db.hands.find()
        self.assertEqual(find_result.count(), 1)
        self.assertEqual(len(find_result[0]["bids"]), 1)
        high_bid_id = find_result[0]["high_bid"]
        high_bid_result = self.dbm.db.bids.find({'_id': high_bid_id})
        self.assertEqual(high_bid_result[0]["bid"], 4)


    def test_publish_hand_results_game_not_over(self):
        self.clear_database_and_dbm()
        self.dbm.create_game(11, 0)
        self.dbm.add_player("player0")
        self.dbm.add_player("player1")
        self.dbm.add_game_to_db_for_first_time()
        self.dbm.create_new_hand()
        self.dbm.add_new_bid("player0", ["AS", "KS", "QS", "JS", "JC", "2S" ], 4, 4, True)
        self.dbm.finalize_hand_creation(False)
        self.dbm.publish_hand_results("Spades", 5, 0, None, None)
        game_result = self.dbm.db.games.find()
        self.assertEqual(game_result.count(), 1)
        self.assertEqual(len(game_result[0]["hands"]), 1)
        bid_result = self.dbm.db.bids.find({'_id': self.dbm.current_bid_record['_id']})
        self.assertEqual(bid_result.count(), 1)
        self.assertEqual(bid_result[0]["points_won"], 5)
        self.assertEqual(bid_result[0]["points_lost"], 0)


    def test_publish_hand_results_game_over(self):
        self.clear_database_and_dbm()
        self.dbm.create_game(11, 0)
        self.dbm.add_player("player0")
        self.dbm.add_player("player1")
        self.dbm.add_game_to_db_for_first_time()
        self.dbm.create_new_hand()
        self.dbm.add_new_bid("player0", ["AS", "KS", "QS", "JS", "JC", "2S" ], 4, 4, True)
        self.dbm.finalize_hand_creation(False)
        results = []
        results.append({ "player": "player0", "team_id": None, "final_score": 11 })
        results.append({ "player": "player1", "team_id": None, "final_score": 3 })
        self.dbm.publish_hand_results("Spades", 5, 0, results, [ "player0" ])
        game_result = self.dbm.db.games.find()
        self.assertEqual(game_result.count(), 1)
        self.assertEqual(len(game_result[0]["hands"]), 1)
        self.assertEqual(game_result[0]["winners"][0], self.dbm.player_map["player0"])
        self.assertEqual(game_result[0]["results"], results)
        bid_result = self.dbm.db.bids.find({'_id': self.dbm.current_bid_record['_id']})
        self.assertEqual(bid_result.count(), 1)
        self.assertEqual(bid_result[0]["points_won"], 5)
        self.assertEqual(bid_result[0]["points_lost"], 0)
