import os
import play_smear_api as smear
import unittest
import tempfile
import json


def post_data_and_return_params(app, url, data):
    rv = app.post(url,
            data=json.dumps(data),
            follow_redirects=True,
            content_type='application/json')
    return json.loads(rv.get_data())


def get_and_return_params(app, url):
    rv = app.get(url, follow_redirects=True)
    return json.loads(rv.get_data())


class PlaySmearGameStartTest(unittest.TestCase):

    def setUp(self):
        smear.app.config['TESTING'] = True
        self.app = smear.app.test_client()
        self.url = "/api/game/start/"

    def tearDown(self):
        pass

    def test_root_url(self):
        rv = self.app.get('/')
        self.assertIn(b'The requested URL was not found on the server.', rv.get_data())

    def test_game_start_get(self):
        rv = self.app.get(self.url)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_game_start_post_empty_json(self):
        rv = self.app.post(self.url, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_start_missing_username(self):
        data = { "numPlayers": 3 }
        rv = self.app.post(self.url,
                data=json.dumps(data),
                follow_redirects=True,
                content_type='application/json')
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_game_start_returns_gameid(self):
        data = { "numPlayers": 3, "username": "matt" }
        params = post_data_and_return_params(self.app, self.url, data)
        self.assertIn("game_id", params)
        game_id = params["game_id"]
        self.assertIsNotNone(game_id)
        self.assertNotEqual(game_id, "")


class PlaySmearGameStartStatusTest(unittest.TestCase):

    def setUp(self):
        smear.app.config['TESTING'] = True
        self.app = smear.app.test_client()
        self.url = "/api/game/startstatus/"
        self.numPlayers = 3
        data = { "numPlayers": self.numPlayers, "username": "matt" }
        params = post_data_and_return_params(self.app, "/api/game/start/", data)
        self.game_id = params["game_id"]

    def tearDown(self):
        pass

    def test_game_startstatus_get_empty(self):
        rv = self.app.get(self.url)
        print rv.get_data()
        self.assertIn(b'404 Not Found', rv.get_data())

    def test_game_startstatus_returns_player_names(self):
        numPlayers = 3
        params = get_and_return_params(self.app, self.url + self.game_id + "/")
        self.assertIn("ready", params)
        ready = params["ready"]
        self.assertTrue(ready)
        self.assertIn("player_names", params)
        player_names = params["player_names"]
        self.assertIsNotNone(player_names)
        self.assertEqual(len(player_names), self.numPlayers)

if __name__ == '__main__':
    unittest.main()
