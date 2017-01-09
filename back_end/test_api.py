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

class PlaySmearStartgameTest(unittest.TestCase):

    def setUp(self):
        smear.app.config['TESTING'] = True
        self.app = smear.app.test_client()
        self.startgame = "/api/startgame/"

    def tearDown(self):
        pass

    def test_root_url(self):
        rv = self.app.get('/')
        self.assertIn(b'The requested URL was not found on the server.', rv.get_data())

    def test_startgame_get(self):
        rv = self.app.get(self.startgame)
        self.assertIn(b'The method is not allowed', rv.get_data())

    def test_startgame_post_empty_json(self):
        rv = self.app.post(self.startgame, follow_redirects=True)
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_startgame_missing_username(self):
        data = { "numPlayers": 3 }
        rv = self.app.post(self.startgame,
                data=json.dumps(data),
                follow_redirects=True,
                content_type='application/json')
        self.assertIn(b'this server could not understand', rv.get_data())

    def test_startgame_returns_gameid(self):
        data = { "numPlayers": 3, "username": "matt" }
        params = post_data_and_return_params(self.app, self.startgame, data)
        self.assertIn("game_id", params)
        game_id = params["game_id"]
        self.assertIsNotNone(game_id)
        self.assertNotEqual(game_id, "")

    def test_startgame_returns_other_players(self):
        numPlayers = 3
        data = { "numPlayers": numPlayers, "username": "matt" }
        params = post_data_and_return_params(self.app, self.startgame, data)
        self.assertIn("other_players", params)
        other_players = params["other_players"]
        self.assertIsNotNone(other_players)
        self.assertEqual(len(other_players), numPlayers - 1)


if __name__ == '__main__':
    unittest.main()
