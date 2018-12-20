import unittest
from mock import MagicMock
import sys

sys.path.insert(0, "..")
from pysmear import smear_engine_api

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
        self.api = smear_engine_api.SmearEngineApi(debug=False)
        self.create_default_mock_smear()

    ####################
    # Tests
    ####################
    def test_create_new_game(self):
        self.api.create_new_game(4, 1)
        self.assertEqual(self.api.desired_players, 4)
        self.assertEqual(self.api.desired_human_players, 1)

    def test_add_player_non_interactive(self):
        self.api.smear.add_player.return_value = None
        self.api.add_player("username", interactive=False)
        args, kwargs = self.api.smear.add_player.call_args
        self.assertEqual(1, len(args))
        self.assertEqual(args[0].name, "username")

    def test_get_hand_results(self):
        self.api.smear.get_hand_results.return_value = {} 
        self.api.get_hand_results("id1")
        args, kwargs = self.api.smear.get_hand_results.call_args
        self.assertEqual(1, len(args))
        self.assertEqual(args[0], "id1")

