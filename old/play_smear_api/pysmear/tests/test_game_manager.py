import unittest
from mock import MagicMock
import sys

sys.path.insert(0, "..")
from pysmear import game_manager
from pysmear import playing_logic
from pysmear import player

class TestSmearEngineApi(unittest.TestCase):
    ####################
    # Helper functions
    ####################
    def create_default_mock_smear(self):
        m = MagicMock()
        #attrs = {'get_player_names.return_value':[ self.username, "user1", "user2" ]}
        #m.configure_mock(**attrs)
        self.api.smear = m

    def add_return_value_to_smear_function(self, function_name, ret):
        attrs = { "{}.return_value".format(function_name): ret }
        self.api.smear.configure_mock(**attrs)

    def assert_smear_function_called_with(self, function_name, *args, **kwargs):
        function = getattr(self.api.smear, function_name)
        function.assert_called_with(*args, **kwargs)

    def setUp(self):
        self.smear = game_manager.SmearGameManager(debug=False)

    ####################
    # Tests
    ####################

    def test_add_player_with_same_name(self):
        player1 = player.Player("username", debug=self.debug, playing_logic=playing_logic.CautiousTaker(debug=self.debug))
        player2 = player.Player("username", debug=self.debug, playing_logic=playing_logic.CautiousTaker(debug=self.debug))
        self.smear.add_player(player1)
        with self.assertRaises(Exception):
            self.smear.add_player(player2)

