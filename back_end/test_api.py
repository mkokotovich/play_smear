import os
import play_smear_api as smear
import unittest
import tempfile
import json


class PlaySmearTest(unittest.TestCase):

    def setUp(self):
        self.app = smear.app.test_client()

    def post_data_and_return_data(self, url, data):
        rv = self.app.post(url,
                data=json.dumps(data),
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


class PlaySmearGameCreateTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        smear.app.config['TESTING'] = True
        self.url = "/api/game/create/"

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
        data = { "numPlayers": 3 }
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("game_id", params)
        game_id = params["game_id"]
        self.assertIsNotNone(game_id)
        self.assertNotEqual(game_id, "")


class PlaySmearGameJoinTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        smear.app.config['TESTING'] = True
        self.url = "/api/game/join/"
        self.numPlayers = 3
        data = { "numPlayers": self.numPlayers }
        params = self.post_data_and_return_data("/api/game/create/", data)
        self.game_id = params["game_id"]
        self.username = "matt"

    def tearDown(self):
        pass

    def test_game_join_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_join_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_join_returns_success(self):
        data = { "game_id": self.game_id, "username": self.username }
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("game_id", params)
        tmp_game_id = params["game_id"]
        self.assertEquals(tmp_game_id, self.game_id)

    def test_game_join_when_already_full_returns_error(self):
        data = { "game_id": self.game_id, "username": self.username }
        # Join the first time
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("game_id", params)
        tmp_game_id = params["game_id"]
        self.assertEquals(tmp_game_id, self.game_id)
        # Join again with a different username
        data = { "game_id": self.game_id, "username": "I_want_to_play_too" }
        status = self.post_data_and_return_status(self.url, data)
        self.assertIn("status_id", status)
        self.assertNotEquals(status["status_id"], 0)
        self.assertIn("message", status)
        self.assertIn("is already full", status["message"])


class PlaySmearGameStartStatusTest(PlaySmearTest):

    def setUp(self):
        PlaySmearTest.setUp(self)
        smear.app.config['TESTING'] = True
        self.url = "/api/game/startstatus/"
        self.numPlayers = 3
        data = { "numPlayers": self.numPlayers }
        params = self.post_data_and_return_data("/api/game/create/", data)
        self.game_id = params["game_id"]
        self.username = "matt"
        data = { "game_id": self.game_id, "username": self.username }
        params = self.post_data_and_return_data("/api/game/join/", data)

    def tearDown(self):
        pass

    def test_game_startstatus_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_startstatus_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_startstatus_returns_player_names(self):
        data = { "game_id": self.game_id, "blocking": True }
        params = self.post_data_and_return_data(self.url, data)
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
        smear.app.config['TESTING'] = True
        self.url = "/api/hand/deal/"
        self.numPlayers = 3
        data = { "numPlayers": self.numPlayers }
        params = self.post_data_and_return_data("/api/game/create/", data)
        self.game_id = params["game_id"]
        self.username = "matt"
        data = { "game_id": self.game_id, "username": self.username }
        params = self.post_data_and_return_data("/api/game/join/", data)
        data = { "game_id": self.game_id, "blocking": True }
        params = self.post_data_and_return_data("/api/game/startstatus/", data)

    def tearDown(self):
        pass

    def test_hand_deal_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_hand_deal_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_hand_deal_returns_list_of_cards(self):
        data = { "game_id": self.game_id, "username": self.username }
        params = self.post_data_and_return_data(self.url, data)
        self.assertIn("cards", params)
        cards = params["cards"]
        self.assertEquals(6, len(cards))


if __name__ == '__main__':
    unittest.main()
