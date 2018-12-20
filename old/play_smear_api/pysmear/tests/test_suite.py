import unittest
import sys
sys.path.insert(0, "..")
sys.path.insert(0, "../pydealer")

from test_bidding_logic import *
from test_playing_logic import *
from test_smear_engine_api import *
from test_smear_utils import *
from test_card_counting import *
from test_game_manager import *
from test_db_manager import *

if __name__ == '__main__':
   unittest.main()
