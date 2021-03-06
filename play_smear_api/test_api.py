import os
import play_smear_api as smear
import unittest
from mock import patch, MagicMock
import tempfile
import json
from pysmear import smear_engine_api
from pysmear import smear_utils
from pysmear import smear_exceptions
import pydealer
import random
import mongomock

# Class with common tools
class PlaySmearTest(unittest.TestCase):

    def setUp(self):
        self.app = smear.app.test_client()
        smear.app.config['TESTING'] = True
        smear.app.config['LOGGER_HANDLER_POLICY'] = "never"
        self.game_id = "1"
        self.username = "matt"
        self.numPlayers = 3
        smear.g_mongo_client = mongomock.MongoClient()


    def post_data_and_return_data(self, url, data):
        rv = self.app.post(url,
                data=json.dumps(data) if data else None,
                follow_redirects=True,
                content_type='application/json')
        result = json.loads(rv.get_data())
        self.assertIn("status", result)
        self.assertEquals(result["status"]["status_id"], 0)
        self.assertIn("data", result)
        return result["data"]

    def post_data_and_return_status(self, url, data):
        rv = self.app.post(url,
                data=json.dumps(data),
                follow_redirects=True,
                content_type='application/json')
        result = json.loads(rv.get_data())
        self.assertIn("status", result)
        return result["status"]

    def get_and_return_params(self, url):
        rv = self.app.get(url, follow_redirects=True)
        result = json.loads(rv.get_data())
        self.assertIn("data", result)
        return result["data"]

    def create_default_mock_engine(self):
        m = MagicMock()
        attrs = {'get_player_names.return_value':[ self.username, "user1", "user2" ],
                 'get_player_who_we_are_waiting_for.return_value':"",
                 'get_team_id_for_player.return_value': None,
                 'get_num_teams.return_value': 0 }
        m.configure_mock(**attrs)
        smear.g_engines[self.game_id] = m

    def add_return_value_to_engine_function(self, function_name, ret):
        attrs = { "{}.return_value".format(function_name): ret }
        smear.g_engines[self.game_id].configure_mock(**attrs)

    def assert_engine_function_called_with(self, function_name, *args, **kwargs):
        function = getattr(smear.g_engines[self.game_id], function_name)
        function.assert_called_with(*args, **kwargs)

    def add_side_effect_to_engine_function(self, function_name, exception):
        attrs = { "{}.side_effect".format(function_name): exception }
        smear.g_engines[self.game_id].configure_mock(**attrs)


class PlaySmearUserLogin(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/user/login/"
        self.email = "smearplayer@gmail.com"
        self.data = { "email": self.email }

    def tearDown(self):
        pass

    def test_user_login_with_email(self):
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("success", params)
        success = params["success"]
        self.assertEqual(success, True)


class PlaySmearUserLogout(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/user/logout/"

    def tearDown(self):
        pass

    def test_user_logout_with_email(self):
        params = self.post_data_and_return_data("/api/user/login/", { "email": "a@b.c" })
        params = self.post_data_and_return_data(self.url, None)
        self.assertIn("success", params)
        success = params["success"]
        self.assertEqual(success, True)


class PlaySmearGameCreateTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/game/create/"
        self.data = { "numPlayers": self.numPlayers, "numHumanPlayers": 0, "pointsToPlayTo": 11, "numTeams": 0 }

    def tearDown(self):
        pass

    def test_root_url(self):
        rv = self.app.get('/')
        self.assertIn(b'The requested URL was not found on the server.', rv.get_data())

    def test_game_create_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_create_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_create_returns_gameid(self):
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("game_id", params)
        game_id = params["game_id"]
        self.assertIsNotNone(game_id)
        self.assertNotEqual(game_id, "")


class PlaySmearGameJoinTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/game/join/"
        self.create_default_mock_engine()
        self.add_return_value_to_engine_function("get_desired_number_of_players", 3)
        self.add_return_value_to_engine_function("get_desired_number_of_human_players", 3)
        self.data = { "game_id": self.game_id, "username": self.username }

    def tearDown(self):
        pass

    def test_game_join_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_join_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_join_returns_success(self):
        self.add_return_value_to_engine_function("all_players_added", False)
        self.add_return_value_to_engine_function("get_number_of_players", self.numPlayers)
        self.add_return_value_to_engine_function("get_points_to_play_to", 11)
        self.add_return_value_to_engine_function("get_graph_prefix", "abcd")
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("game_id", params)
        tmp_game_id = params["game_id"]
        self.assertEquals(tmp_game_id, self.game_id)

    def test_game_join_when_already_full_returns_error(self):
        self.add_return_value_to_engine_function("all_players_added", False)
        self.add_return_value_to_engine_function("get_number_of_players", self.numPlayers)
        self.add_return_value_to_engine_function("get_points_to_play_to", 11)
        self.add_return_value_to_engine_function("get_graph_prefix", "abcd")
        data = { "game_id": self.game_id, "username": self.username }
        # Join the first time
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("game_id", params)
        tmp_game_id = params["game_id"]
        self.assertEquals(tmp_game_id, self.game_id)
        # Join again with a different username
        self.add_return_value_to_engine_function("all_players_added", True)
        data = { "game_id": self.game_id, "username": "I_want_to_play_too" }
        status = self.post_data_and_return_status(self.url, data)
        self.assertIn("status_id", status)
        self.assertNotEquals(status["status_id"], 0)
        self.assertIn("message", status)
        self.assertIn("is already full", status["message"])

    def test_game_join_with_name_already_in_use(self):
        self.add_return_value_to_engine_function("all_players_added", False)
        self.add_return_value_to_engine_function("get_number_of_players", self.numPlayers)
        self.add_return_value_to_engine_function("get_points_to_play_to", 11)
        self.add_return_value_to_engine_function("get_graph_prefix", "abcd")
        data = { "game_id": self.game_id, "username": self.username }
        # Join the first time
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("game_id", params)
        tmp_game_id = params["game_id"]
        self.assertEquals(tmp_game_id, self.game_id)
        # Join again with a different username
        self.add_side_effect_to_engine_function("add_player", smear_exceptions.SmearUserHasSameName("The name {} is already taken, choose a different name".format(self.username)))
        data = { "game_id": self.game_id, "username": self.username }
        status = self.post_data_and_return_status(self.url, data)
        self.assertIn("status_id", status)
        self.assertNotEquals(status["status_id"], 0)
        self.assertIn("message", status)
        self.assertIn("is already taken", status["message"])


class PlaySmearGameStartStatusTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/game/startstatus/"
        self.create_default_mock_engine()
        self.data = { "game_id": self.game_id, "username": self.username }

    def tearDown(self):
        pass

    def test_game_startstatus_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_startstatus_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_startstatus_returns_player_names(self):
        self.add_return_value_to_engine_function("all_players_added", True)
        self.add_return_value_to_engine_function("game_is_started", True)
        self.add_return_value_to_engine_function("get_desired_number_of_players", self.numPlayers)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("ready", params)
        ready = params["ready"]
        self.assertTrue(ready)
        self.assertIn("player_names", params)
        player_names = params["player_names"]
        self.assertIsNotNone(player_names)
        self.assertEqual(len(player_names), self.numPlayers)
        self.assertIn("num_players", params)
        num_players = params["num_players"]
        self.assertEqual(num_players, self.numPlayers)



class PlaySmearHandDealTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/deal/"
        self.create_default_mock_engine()
        self.data = { "game_id": self.game_id, "username": self.username }

    def tearDown(self):
        pass

    def test_hand_deal_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_deal_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_hand_deal_returns_list_of_cards(self):
        cards = [ 
                { "suit":"spades", "value": "2" },
                { "suit":"clubs", "value": "3" },
                { "suit":"diamonds", "value": "4" },
                { "suit":"hearts", "value": "5" },
                { "suit":"spades", "value": "10" },
                { "suit":"spades", "value": "Ace" }
                ]
        hand_id = 0
        self.add_return_value_to_engine_function("get_hand_for_player", cards)
        self.add_return_value_to_engine_function("get_hand_id", hand_id)
        params = self.post_data_and_return_data(self.url, self.data)
        ret_cards = params["cards"]
        self.assertEquals(6, len(ret_cards))
        for i in range(0, 6):
            self.assertEquals(cards[i], ret_cards[i])
        self.assertEquals(hand_id, params["hand_id"])


class PlaySmearHandGetBidInfoTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/getbidinfo/"
        self.data = { "game_id": self.game_id, "username": self.username }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_get_bid_info_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_get_bid_info_returns_bid_info(self):
        bid_info = { 
                'force_two': False,
                'dealer': "user01",
                'ready_to_bid': True,
                'current_bid': 2,
                'bidder': "user01",
                'all_bids': [
                    { 'game_id': self.game_id,
                      'username': "user01",
                      'bid': 2
                    },
                    { 'game_id': self.game_id,
                      'username': "user02",
                      'bid': 0
                    }
                    ]
                }
        self.add_return_value_to_engine_function("get_bid_info_for_player", bid_info)
        self.add_return_value_to_engine_function("get_dealer", "user01")
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_bid_info_for_player", self.username)
        for key, value in bid_info.items():
            self.assertIn(key, params)
            self.assertEquals(value, params[key])


class PlaySmearHandSubmitBid(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/submitbid/"
        self.bid = 3
        self.data = { "game_id": self.game_id, "username": self.username, "bid": self.bid }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_submit_bid_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_submit_bid_returns_success(self):
        self.add_return_value_to_engine_function("submit_bid_for_player", True)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("submit_bid_for_player", self.username, self.bid)


class PlaySmearHandGetHighBid(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/gethighbid/"
        self.high_bid = 4
        self.high_bidder = "bidder"
        self.high_bid_info = { 
                'force_two': False,
                'current_bid': self.high_bid,
                'bidder': self.high_bidder,
                'all_bids': [
                    { 'game_id': self.game_id,
                      'username': "user01",
                      'bid': 2
                    },
                    { 'game_id': self.game_id,
                      'username': self.high_bidder,
                      'bid': self.high_bid
                    },
                    { 'game_id': self.game_id,
                      'username': "user02",
                      'bid': 0
                    }
                    ]
                }
        self.hand_id = 0
        self.data = { "game_id": self.game_id, "hand_id": self.hand_id }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_get_high_bid_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_get_high_bid_returns_correct_high_bid_and_bidder(self):
        self.add_return_value_to_engine_function("get_high_bid", self.high_bid_info)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_high_bid", self.hand_id)
        for key, value in self.high_bid_info.items():
            self.assertIn(key, params)
            self.assertEquals(value, params[key])


class PlaySmearHandGetTrump(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/gettrump/"
        self.trump = "Spades"
        self.data = { "game_id": self.game_id, "username": self.username, "trump": self.trump }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_get_trump_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_get_trump_returns_correct_trump_with_empty_trump(self):
        self.data["trump"] = ""
        self.add_return_value_to_engine_function("get_trump", self.trump)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_trump")
        self.assertIn("trump", params)
        self.assertEqual(params["trump"], self.trump)

    def test_hand_get_trump_returns_correct_trump_with_chosen_trump(self):
        self.data["trump"] = self.trump
        self.add_return_value_to_engine_function("submit_trump_for_player", True)
        self.add_return_value_to_engine_function("get_trump", self.trump)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("submit_trump_for_player", self.username, self.trump)
        self.assert_engine_function_called_with("get_trump")
        self.assertIn("trump", params)
        self.assertEqual(params["trump"], self.trump)


class PlaySmearHandGetPlayingInfo(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/getplayinginfo/"
        self.cards_played = [ 
                { "username": "player1", "card": { "suit":"Spades", "value": "2" }},
                { "username": "player2", "card": { "suit":"Spades", "value": "Ace" }}
                ]
        self.lead_suit = "Spades"
        self.current_winning_card = { "suit": "Spades", "value": "Ace" }
        self.playing_info = { 
                "cards_played" : self.cards_played,
                "current_winning_card": self.current_winning_card,
                "lead_suit": self.lead_suit
                }
        self.data = { "game_id": self.game_id, "username": self.username }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_get_playing_info_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_get_playing_info_with_two_cards_in_trick(self):
        self.add_return_value_to_engine_function("get_playing_info_for_player", self.playing_info)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_playing_info_for_player", self.username)
        self.assertIn("cards_played", params)
        self.assertEqual(params["cards_played"], self.cards_played)
        self.assertIn("current_winning_card", params)
        self.assertEqual(params["current_winning_card"], self.current_winning_card)
        self.assertIn("lead_suit", params)
        self.assertEqual(params["lead_suit"], self.lead_suit)

    def test_hand_get_playing_info_when_no_cards_have_been_played(self):
        empty_trick = []
        empty_suit = ""
        empty_winning_card = { "suit": "", "value": "" }
        empty_playing_info = { 
                "cards_played" : empty_trick,
                "current_winning_card": empty_winning_card,
                "lead_suit": empty_suit
                }
        self.add_return_value_to_engine_function("get_playing_info_for_player", empty_playing_info)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_playing_info_for_player", self.username)
        self.assertIn("cards_played", params)
        self.assertEqual(params["cards_played"], empty_trick)
        self.assertIn("current_winning_card", params)
        self.assertEqual(params["current_winning_card"], empty_winning_card)
        self.assertIn("lead_suit", params)
        self.assertEqual(params["lead_suit"], empty_suit)


class PlaySmearHandSubmitCardToPlay(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/submitcard/"
        self.card_to_play = { "suit": "Spades", "value": "Ace" }
        self.data = { "game_id": self.game_id, "username": self.username, "card_to_play": self.card_to_play }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_submit_card_to_play_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_submit_card_to_play_returns_success(self):
        self.add_return_value_to_engine_function("submit_card_to_play_for_player", True)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("submit_card_to_play_for_player", self.username, self.card_to_play)

    def test_hand_submit_card_to_play_with_invalid_card(self):
        invalid_card_to_play = { "suite": "Spades", "number": "Ace" }
        invalid_data = { "game_id": self.game_id, "username": self.username, "card_to_play": invalid_card_to_play }
        status = self.post_data_and_return_status(self.url, invalid_data)
        self.assertIn("status_id", status)
        self.assertNotEquals(status["status_id"], 0)
        self.assertIn("message", status)
        self.assertIn("Improperly formatted card", status["message"])


class PlaySmearHandGetTrickResults(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/gettrickresults/"
        self.trick_results = { 
                "winner": self.username,
                "cards_played": [
                    { "username": self.username, "card": {"suit": "Spades", "value": "Ace"}},
                    { "username": "player1", "card": {"suit": "Hearts", "value": "3"}},
                    { "username": "player2", "card": {"suit": "Spades", "value": "Jack"}},
                    ]
                }
        self.data = { "game_id": self.game_id, "username": self.username }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_submit_card_to_play_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_submit_card_to_play_returns_success(self):
        self.add_return_value_to_engine_function("get_trick_results_for_player", self.trick_results)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_trick_results_for_player", self.username)


class PlaySmearHandGetResults(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.url = "/api/hand/getresults/"
        self.hand_id = 1
        self.hand_results = { 
                "high_winner": self.username,
                "low_winner": self.username,
                "jack_winner": self.username,
                "jick_winner": self.username,
                "game_winner": self.username,
                "is_game_over": False,
                "player_infos": [
                    { "username": "player1", "score": 0 },
                    { "username": "player2", "score": -2 },
                    { "username": "player3", "score": 3 }
                    ]
                }
        self.data = { "game_id": self.game_id, "hand_id": self.hand_id, "username": self.username }
        self.create_default_mock_engine()

    def tearDown(self):
        pass

    def test_hand_submit_card_to_play_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_submit_card_to_play_returns_success_does_not_end_if_not_finished(self):
        self.hand_results["is_game_over"] = False
        self.add_return_value_to_engine_function("get_hand_results", self.hand_results)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_hand_results", self.hand_id)

    def test_hand_submit_card_to_play_returns_success_calls_player_finished_if_finished(self):
        self.hand_results["is_game_over"] = True
        self.add_return_value_to_engine_function("get_hand_results", self.hand_results)
        self.add_return_value_to_engine_function("player_is_finished", False)
        params = self.post_data_and_return_data(self.url, self.data)
        self.assert_engine_function_called_with("get_hand_results", self.hand_id)
        self.assert_engine_function_called_with("player_is_finished", self.username)



class PlaySmearEndToEnd(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        self.cards = {}
        self.game_id = ""

        # Overwrite these 
        self.players = [ "p1", "p2", "p3" ]
        self.numPlayers = 3
        self.points_to_play_to = 5
        self.num_teams = 0

        # Change this to enable logging
        self.engineDebug = False

    def tearDown(self):
        pass

    def create_and_join_game(self):
        # Create game
        self.url = "/api/game/create/"
        self.data = {
                "numPlayers": self.numPlayers,
                "numHumanPlayers": self.numPlayers,
                "pointsToPlayTo": self.points_to_play_to,
                "engineDebug": self.engineDebug,
                "numTeams": self.num_teams
                }
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("game_id", params)
        self.game_id = params["game_id"]
        self.assertIsNotNone(self.game_id)
        self.assertNotEqual(self.game_id, "")

        # Join Game 
        for player in self.players:
            self.url = "/api/game/join/"
            self.data = { "game_id": self.game_id, "username": player }
            params = self.post_data_and_return_data(self.url, self.data)
            self.assertIn("game_id", params)
            self.assertEqual(params["game_id"], self.game_id)

        # Check if game is ready (it shouldn't be)
        self.url = "/api/game/startstatus/"
        self.data = { "game_id": self.game_id, "username": player }
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("ready", params)
        self.assertFalse(params["ready"])

        # Set the teams to something random
        if self.num_teams != 0:
            player_team_list = []
            team_spots_left = {}
            initial_team_size = self.numPlayers / self.num_teams
            for team_id in range(0, self.num_teams):
                team_spots_left[team_id] = initial_team_size
            for player in self.players:
                pt = {}
                pt["player"] = player
                team_id = None
                while team_id == None:
                    possible_team_id = random.choice(range(0, self.num_teams))
                    if team_spots_left[possible_team_id] > 0:
                        team_id = possible_team_id
                        team_spots_left[team_id] -= 1
                pt["team_id"] = team_id
                player_team_list.append(pt)
            self.url = "/api/game/setteams/"
            self.data = { "game_id": self.game_id, "player_team_list": player_team_list }
            params = self.post_data_and_return_data(self.url, self.data)

        # Start game
        self.url = "/api/game/start/"
        self.data = { "game_id": self.game_id }
        params = self.post_data_and_return_data(self.url, self.data)

        # Check if game is ready (now it should be)
        self.url = "/api/game/startstatus/"
        self.data = { "game_id": self.game_id, "username": player }
        params = self.post_data_and_return_data(self.url, self.data)
        self.assertIn("ready", params)
        self.assertTrue(params["ready"])
        self.assertIn("player_names", params)
        player_names = params["player_names"]
        self.assertIsNotNone(player_names)
        self.assertEqual(len(player_names), self.numPlayers)
        self.assertIn("num_players", params)
        num_players = params["num_players"]
        self.assertEqual(num_players, self.numPlayers)

    def play_hand(self):
        # Deal cards
        for player in self.players:
            self.url = "/api/hand/deal/"
            self.data = { "game_id": self.game_id, "username": player }
            params = self.post_data_and_return_data(self.url, self.data)
            self.cards[player] = pydealer.Stack()
            for card in params["cards"]:
                self.cards[player].add(pydealer.Card(card["value"], card["suit"]))
            self.assertEquals(6, len(self.cards[player]))
            self.hand_id = params["hand_id"]

        player_bidder = random.choice(self.players)
        for bidder in range(0, self.numPlayers):
            # Get bid info
            self.url = "/api/hand/getbidinfo/"
            self.data = { "game_id": self.game_id, "username": self.players[bidder] }
            params = self.post_data_and_return_data(self.url, self.data)

            # Submit bid
            self.url = "/api/hand/submitbid/"
            self.bid = 0
            if self.players[bidder] == player_bidder:
                self.bid = 3
            self.data = { "game_id": self.game_id, "username": self.players[bidder], "bid": self.bid }
            params = self.post_data_and_return_data(self.url, self.data)


        # Get high bid
        for player in self.players:
            self.url = "/api/hand/gethighbid/"
            self.data = { "game_id": self.game_id, "hand_id": self.hand_id }
            params = self.post_data_and_return_data(self.url, self.data)
            self.assertIn("bidder", params)
            self.assertEquals(params["bidder"], player_bidder)
            self.assertIn("current_bid", params)
            self.assertEquals(params["current_bid"], 3)

        # Submit trump
        self.url = "/api/hand/gettrump/"
        self.trump = random.choice( [ "Spades", "Clubs", "Diamonds", "Hearts" ] )
        self.data = { "game_id": self.game_id, "username": player_bidder, "trump": self.trump }
        params = self.post_data_and_return_data(self.url, self.data)

        # Get trump
        for player in self.players:
            self.url = "/api/hand/gettrump/"
            self.data = { "game_id": self.game_id, "username": player, "trump": None }
            params = self.post_data_and_return_data(self.url, self.data)

        # Play hand
        for trick in range(0, 6):
            # For a trick, first get playing info and then submit a card
            card_played = []
            while len(card_played) < self.numPlayers:
                for player in self.players:
                    # Skip if he's already played
                    if player in card_played:
                        continue

                    # Get playing info
                    self.url = "/api/hand/getplayinginfo/"
                    self.data = { "game_id": self.game_id, "username": player }
                    params = self.post_data_and_return_data(self.url, self.data)

                    # only submit card if it is ready for his turn
                    if not params["ready_to_play"]:
                        continue

                    # Submit card to play
                    self.url = "/api/hand/submitcard/"
                    indices = smear_utils.SmearUtils.get_legal_play_indices(params["lead_suit"], self.trump, self.cards[player])
                    card_index = random.choice(indices)
                    # Pick a random card
                    card = self.cards[player][card_index]
                    self.card_to_play = { "suit": card.suit, "value": card.value }
                    del self.cards[player][card_index]
                    self.data = { "game_id": self.game_id, "username": player, "card_to_play": self.card_to_play }
                    params = self.post_data_and_return_data(self.url, self.data)
                    card_played.append(player)

            # Get the results of the trick
            for player in self.players:
                self.url = "/api/hand/gettrickresults/"
                self.data = { "game_id": self.game_id, "username": player }
                params = self.post_data_and_return_data(self.url, self.data)

        # Get results of hand
        game_over = False
        for player in self.players:
            self.url = "/api/hand/getresults/"
            self.data = { "game_id": self.game_id, "hand_id": self.hand_id, "username": player }
            params = self.post_data_and_return_data(self.url, self.data)
            self.assertIn("is_game_over", params)
            if params["is_game_over"]:
                game_over = True

        return game_over


    def play_game(self):
        self.create_and_join_game()
        game_over = False
        while not game_over:
            game_over = self.play_hand()



# Three person cut-throat
class PlaySmearBrothersTest(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Adam", "Tim" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 0

    def tearDown(self):
        pass

    def test_brothers_usecase(self):
        self.play_game()


# 2v2 teams
class PlaySmearFamilyTest(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Adam", "Tim", "Dad" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 2

    def tearDown(self):
        pass

    def test_family_game(self):
        self.play_game()


# 3 teams of 2
class PlaySmearThreeTeam(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Adam", "Tim", "Cari", "Katie", "Brittany" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 3

    def tearDown(self):
        pass

    def test_3_teams_of_2(self):
        self.play_game()


# 2 teams of 3
class PlaySmearTwoTeamsOfThree(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Adam", "Tim", "Cari", "Katie", "Brittany" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 2

    def tearDown(self):
        pass

    def test_2_teams_of_3(self):
        self.play_game()


# 2 person smear
class PlaySmearTwoPeople(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Eli" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 0

    def tearDown(self):
        pass

    def test_2_person_smear(self):
        self.play_game()


# 2 teams of 4
class PlaySmearTwoTeamsOfFour(PlaySmearEndToEnd):

    def setUp(self):
        PlaySmearEndToEnd.setUp(self)
        self.players = [ "Matt", "Adam", "Tim", "Cari", "Katie", "Brittany", "Steve", "Barb" ]
        self.numPlayers = len(self.players)
        self.points_to_play_to = 5
        self.num_teams = 2

    def tearDown(self):
        pass

    def test_2_teams_of_4(self):
        self.play_game()
if __name__ == '__main__':
    unittest.main()
