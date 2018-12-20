# API for playing the card game smear

import sys
from threading import Thread, Event
import Queue
from game_manager import *
from player import *
from playing_logic import *
from bidding_logic import *
from smear_exceptions import *
from db_manager import *


class SmearEngineApi:
    def __init__(self, debug=False):
        self.smear = None
        self.debug = debug
        self.desired_players = 0
        self.desired_human_players = 0
        self.number_of_interactive_players = 0
        self.players_who_are_finished = []
        self.game_started = False
        self.game_finished = False
        self.static_dir =  None
        self.graph_prefix = None 
        self.dbm = None


    def set_graph_details(self, path_to_static, graph_prefix):
        self.static_dir = path_to_static
        self.graph_prefix = graph_prefix

    
    def get_graph_prefix(self):
        return self.graph_prefix


    def set_game_stats_database_details(self, hostname=None, port=None, client=None, database=None):
        if client:
            self.dbm = DbManager(database=database, client=client, debug=self.debug)
        else:
            self.dbm = DbManager(database=database, hostname=hostname, port=port, debug=self.debug)


    def create_new_game(self, num_players, num_human_players, cards_to_deal=6, score_to_play_to=11, num_teams=0):
        self.smear = SmearGameManager(cards_to_deal=cards_to_deal, score_to_play_to=score_to_play_to, num_teams=num_teams, debug=self.debug, graph_prefix=self.graph_prefix, static_dir=self.static_dir, dbm=self.dbm)
        self.desired_players = num_players
        self.desired_human_players = num_human_players


    def add_player(self, username, email=None, interactive=False):
        if interactive:
            self.smear.add_player(InteractivePlayer(username, debug=self.debug), email)
            self.number_of_interactive_players += 1
        else:
            self.smear.add_player(Player(username, debug=self.debug, playing_logic=CautiousTaker(debug=self.debug), bidding_logic=BetterBidding(debug=self.debug)))


    def change_player_team(self, player_name, new_team_id):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        player.team_id = new_team_id


    def update_player_orders(self):
        self.smear.reorder_players_by_team()


    def all_players_added(self):
        return self.desired_players == len(self.smear.get_players())


    def game_is_started(self):
        return self.game_started


    def all_human_players_joined(self):
        return self.desired_human_players == self.number_of_interactive_players


    def get_desired_number_of_players(self):
        return self.desired_players


    def get_desired_number_of_human_players(self):
        return self.desired_human_players


    def get_player_names(self):
        names = [ x.name for x in self.smear.get_players() ]
        return names


    def get_team_id_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        return player.team_id


    def get_num_teams(self):
        return self.smear.num_teams


    def get_points_to_play_to(self):
        return self.smear.score_to_play_to


    def start_game(self):
        if self.debug:
            print "\n\n Starting game \n"
        if not self.all_players_added():
            print "Error: Can't start game before all players are added"
            return
        if self.debug:
            print "Number of players: " + str(len(self.smear.get_players()))
        self.smear.reset_game()
        self.smear.start_game()
        self.game_started = True

    
    def continue_game(self):
        if self.game_started and not self.game_finished:
            self.game_finished = self.smear.play_game_async()


    def player_is_finished(self, player_name):
        ready_to_delete = False
        if player_name not in self.players_who_are_finished:
            self.players_who_are_finished.append(player_name)
        if len(self.players_who_are_finished) == self.number_of_interactive_players:
            ready_to_delete = True
        return ready_to_delete


    def finish_game(self):
        if self.debug:
            print "Finishing game"

    
    def get_hand_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        cards = player.get_hand()
        return cards


    def get_hand_id(self):
        return self.smear.get_hand_id()


    def get_dealer(self):
        dealer_id = self.smear.dealer
        dealer_name = self.smear.get_players()[dealer_id].name
        return dealer_name


    def get_bids_submitted_so_far(self):
        all_bids = None
        try:
            all_bids = self.smear.hand_manager.current_hand.get_all_bids()
        except:
            pass

        if all_bids is not None:
            # populate the usernames since we have that info here
            for i in range(0, len(all_bids)):
                player_id = all_bids[i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    all_bids[i]["username"] = player_name

        return all_bids


    def get_player_who_we_are_waiting_for(self, bidding):
        player_id = None
        previous_player = None
        if bidding:
            all_bids = self.smear.hand_manager.current_hand.get_all_bids()
            if len(all_bids) == 0:
                player_id = self.smear.hand_manager.next_player_id(self.smear.dealer)
            elif len(all_bids) == self.desired_players:
                player_id = self.smear.hand_manager.current_hand.bidder
            else:
                previous_player = all_bids[-1]["username"]
        else:
            cards_played = self.smear.hand_manager.current_hand.get_cards_played()
            if len(cards_played) == 0:
                player_id = self.smear.hand_manager.current_hand.first_player
            elif len(cards_played) == self.desired_players:
                player_id = ""
            else:
                previous_player = cards_played[-1]["username"]

        if player_id is None:
            # We don't know if previous_player will be a string or an id
            previous_player_id = previous_player
            if type(0) != type(previous_player):
                player_name_list = [ player.name for player in self.smear.hand_manager.get_players() ]
                previous_player_id = player_name_list.index(previous_player)
            player_id = self.smear.hand_manager.next_player_id(previous_player_id)

        # populate the username since we have that info here
        player_name = player_id
        if type(0) == type(player_id):
            player_name = self.smear.get_players()[player_id].name

        return player_name


    def get_bid_info_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        bid_info = player.get_bid_info()
        if bid_info == None:
            return None

        # populate the username since we have that info here
        player_id = bid_info["bidder"]
        if type(0) == type(player_id):
            player_name = self.smear.get_players()[player_id].name
            bid_info["bidder"] = player_name
            for i in range(0, len(bid_info["all_bids"])):
                player_id = bid_info["all_bids"][i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    bid_info["all_bids"][i]["username"] = player_name
        return bid_info


    def submit_bid_for_player(self, player_name, bid):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return False
        player.save_bid(bid)
        return True


    def get_high_bid(self, hand_id):
        player_id = 0
        bids_are_in = self.smear.all_bids_are_in(hand_id)
        if not bids_are_in:
            return None

        high_bid_info = self.smear.get_high_bid_info(hand_id)
        high_bid_info['force_two'] = False

        # populate the usernames since we have that info here
        player_id = high_bid_info["bidder"]
        if type(0) == type(player_id):
            high_bid_info['bidder'] = self.smear.get_players()[player_id].name

        for i in range(0, len(high_bid_info["all_bids"])):
            player_id = high_bid_info["all_bids"][i]["username"]
            if type(0) == type(player_id):
                player_name = self.smear.get_players()[player_id].name
                high_bid_info["all_bids"][i]["username"] = player_name

        return high_bid_info


    def get_trump(self):
        trump = self.smear.get_trump()
        return trump


    def submit_trump_for_player(self, player_name, trump):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return False
        if not player.save_trump(trump):
            print "Error: unable to submit trump {}".format(trump)
            return False
        return True


    def get_cards_played_so_far(self):
        cards_played = None
        try:
            cards_played = self.smear.hand_manager.current_hand.current_trick.get_cards_played()
        except:
            pass

        if cards_played is not None:
            # populate the usernames since we have that info here
            for i in range(0, len(cards_played)):
                player_id = cards_played[i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    cards_played[i]["username"] = player_name

        return cards_played


    def get_playing_info_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        playing_info = player.get_playing_info()
        if playing_info == None:
            return playing_info

        # populate the usernames since we have that info here
        for i in range(0, len(playing_info["cards_played"])):
            player_id = playing_info["cards_played"][i]["username"]
            if type(0) == type(player_id):
                player_name = self.smear.get_players()[player_id].name
                playing_info["cards_played"][i]["username"] = player_name

        return playing_info


    def submit_card_to_play_for_player(self, player_name, card_to_play):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return False
        if not player.save_card_to_play(card_to_play, self.smear.get_trump()):
            print "Error: unable to play {}".format(str(card_to_play))
            return False
        return True


    def get_trick_results_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        trick_results = player.get_results_of_trick()
        if trick_results == None:
            return None

        # populate the usernames since we have that info here
        player_id = trick_results["winner"]
        if type(0) == type(player_id):
            player_name = self.smear.get_players()[player_id].name
            trick_results["winner"] = player_name
            for i in range(0, len(trick_results["cards_played"])):
                player_id = trick_results["cards_played"][i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    trick_results["cards_played"][i]["username"] = player_name

        return trick_results


    def get_hand_results(self, hand_id):
        args = ( hand_id, )
        hand_results = self.smear.get_hand_results(hand_id)
        if hand_results == None:
            return hand_results

        # populate the usernames since we have that info here
        for key, value in hand_results.items():
            if "winner" in key:
                player_id = value
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    hand_results[key] = player_name
            elif "player_infos" == key:
                for pinfo in value:
                    player_id = pinfo["username"]
                    if type(0) == type(player_id):
                        player_name = self.smear.get_players()[player_id].name
                        pinfo["username"] = player_name
            
        return hand_results


    def get_hint_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        card_to_play = self.smear.hand_manager.get_hint_from_computer(player.player_id)
        return { "suit": card_to_play.suit, "value": card_to_play.value }


    def get_bid_hint_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        bid_hint = self.smear.hand_manager.get_bid_hint_from_computer(player.player_id, self.smear.dealer)
        return bid_hint

