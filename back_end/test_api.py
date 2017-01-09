import os
import play_smear_api as smear
import unittest
import tempfile

class PlaySmearApiTestCase(unittest.TestCase):

    def setUp(self):
        smear.app.config['TESTING'] = True
        self.app = smear.app.test_client()
        self.startgame = "/api/startgame/"

    def tearDown(self):
        pass

    def test_root_url(self):
        rv = self.app.get('/')
        assert b'The requested URL was not found on the server.' in rv.data

    def test_startgame_get(self):
        rv = self.app.get(self.startgame)
        assert b'The method is not allowed' in rv.data

    def test_startgame_post_empty_json(self):
        rv = self.app.post(self.startgame, follow_redirects=True)
        assert b'this server could not understand' in rv.data

    def test_startgame_missing_username(self):
        data = { "numPlayers": 3 }
        rv = self.app.post(self.startgame, data=data, follow_redirects=True)
        assert b'this server could not understand' in rv.data

    def test_startgame_success(self):
        data = { "numPlayers": 3, "username": "matt" }
        rv = self.app.post(self.startgame, data=data, follow_redirects=True)
        print str(rv.data)
        assert b'game_id' in rv.data


if __name__ == '__main__':
    unittest.main()
