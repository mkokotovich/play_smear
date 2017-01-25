from flask import Flask, abort, request
from flask_cors import CORS, cross_origin
import json
import threading
import time
from pysmear import smear_engine_api

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

g_game_id = 0
g_game_id_lock = threading.Lock()
g_engines = {}


def generate_error(status_id, message, error_code=500):
    app.logger.error("Returning error: {} ({})".format(message, status_id))
    status = {}
    status["status_id"] = status_id
    status["message"] = message
    ret = {}
    ret["status"] = status
    ret["error"] = message
    return json.dumps(ret), error_code


def generate_return_string(data=None):
    app.logger.debug("Returning success with data: {}".format(str(data)))
    status = {}
    status["status_id"] = 0
    ret = {}
    ret["status"] = status
    ret["data"] = data
    return json.dumps(ret)


def create_game_and_return_id():
    global g_game_id_lock
    global g_game_id
    game_id = None
    g_game_id_lock.acquire()
    try:
        g_game_id += 1
        game_id = str(g_game_id)
    finally:
        g_game_id_lock.release()
    g_engines[game_id] = smear_engine_api.SmearEngineApi(debug=True)
    return game_id


def get_params_or_abort(request):
    params = request.get_json()
    if not params:
        app.logger.error("Empty json parameters, invalid request")
        abort(400)
    return params


def get_value_from_params(params, key, abort_if_absent=True):
    value = None
    if key not in params:
        if abort_if_absent:
            app.logger.error("Missing key ({}) in params: {}".format(key, str(params)))
            abort(400)
        else:
            app.logger.debug("Key ({}) was not found in params ({}), ignoring because abort_if_absent is false".format(key, str(params)))
    else:
        value = params[key]
    return value


# Checks on the status of a game
# Input (json data from post):
#  game_id    - String - ID of game to check on
#  blocking   - boolean - if true, don't return until game is ready to start
# Return (json data):
#  ready        - String/bool  - If the game is ready to start (all players have joined)
#  num_players  - int     - if ready == True, this will be the number of players in the game
#  player_names - list of strings  - if ready == True, this will be a list of all players in the game
@app.route("/api/game/startstatus/", methods=["POST"])
def game_start_status():
    global g_engines

    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    blocking = get_value_from_params(params, "blocking")

    player_names = []
    data = {}
    data["ready"] = g_engines[game_id].all_players_added()
    if blocking:
        sleep_interval = 5
        time_waited = 0
        timeout_after = 600
        while not data["ready"] and time_waited < timeout_after:
            #sleep and check again
            time.sleep(sleep_interval)
            time_waited += sleep_interval
            data["ready"] = g_engines[game_id].all_players_added()
        if time_waited >= timeout_after:
            return generate_error(2, "Game {} took too long, giving up. Create a new game and try again".format(game_id))

    if data["ready"]:
        player_names = g_engines[game_id].get_player_names()
        g_engines[game_id].start_game()
        
    data["num_players"] = len(player_names)
    data["player_names"] = player_names
    return generate_return_string(data)


# join a game
# Input (json data from post):
#  game_id  - string - ID of game to join
#  username - string - username to use
# Return - nothing
@app.route("/api/game/join/", methods=["POST"])
def join_game():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Perform game-related logic
    if g_engines[game_id].all_players_added():
        # Game is already full
        num_players = g_engines[game_id].get_number_of_players()
        return generate_error(1, "Game {} is already full, contains {} players".format(game_id, num_players))

    g_engines[game_id].add_player(player_id=username, interactive=True)
    num_players = g_engines[game_id].get_number_of_players()
    for i in range(1, num_players):
        new_player = "player{}".format(i)
        app.logger.debug("Adding player {} to game {}".format(new_player, game_id))
        g_engines[game_id].add_player(player_id=new_player, interactive=False)

    # Return result
    data = {}
    data["game_id"] = game_id
    return generate_return_string(data)

# creates a new game
# Input (json data from post):
#  numPlayers - Integer - number of players in the game
# Return (json data):
#  game_id    - String  - Id of the game to be used in future API calls
@app.route("/api/game/create/", methods=["POST"])
def create_game():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    numPlayerInput = get_value_from_params(params, "numPlayers")
    numPlayers = 0
    try:
        numPlayers = int(numPlayerInput)
        if numPlayers < 2 or numPlayers > 8:
            raise ValueError("Invalid number of players")
    except ValueError:
        return generate_error(3, "Invalid number of players {}, must be between 2 and 8".format(numPlayerInput))

    # Perform game-related logic
    game_id = create_game_and_return_id()
    app.logger.debug("Starting game {} with {} players".format(game_id, numPlayers))
    g_engines[game_id].create_new_game(num_players=numPlayers)

    # Return result
    data = {}
    data["game_id"] = game_id
    return generate_return_string(data)


# Receive the deal for the next hand
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  cards    - array of cards - player "username"s hand
#  hand_id  - string         - ID of the hand we're playing
@app.route("/api/hand/deal/", methods=["POST"])
def get_next_deal():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Perform game-related logic
    cards = g_engines[game_id].get_hand_for_player(username) 
    hand_id = g_engines[game_id].get_hand_id() 

    # Return result, cards list should be at the root of data
    data = {}
    data["cards"] = cards
    data["hand_id"] = hand_id
    return generate_return_string(data)


# Return the bid info for the player
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  bid_info - information pertaining to the current bid
@app.route("/api/hand/getbidinfo/", methods=["POST"])
def get_bid_info():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Perform game-related logic
    bid_info = g_engines[game_id].get_bid_info_for_player(username) 

    # Return result, bid_info dict should be the top-level data
    data = bid_info
    return generate_return_string(data)


# Submit player's bid
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
#  bid      - int    - player's bid
# Return (json data):
#  nothing, just status
@app.route("/api/hand/submitbid/", methods=["POST"])
def submit_bid():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")
    bid_input = str(get_value_from_params(params, "bid"))
    bid = 0

    # Check input
    if bid_input.lower() == "pass":
        bid = 0
    else:
        try:
            bid = int(bid_input)
            if bid < 0 or bid == 1 or bid > 5:
                raise ValueError("Invalid bid")
        except ValueError:
            return generate_error(6, "Invalid bid: {}, bid must be between 2 and 5, or 0 for a pass".format(bid))
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Perform game-related logic
    valid_bid = g_engines[game_id].submit_bid_for_player(username, bid) 
    if not valid_bid:
        return generate_error(6, "Invalid bid ({}) for {}, unable to submit bid".format(bid, username))

    # Return success
    return generate_return_string()


# Find out who the high bidder is, and what the bid is (not including trump, though)
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  hand_id  - string - ID of hand we're playing
# Return (json data):
#  username - string - username of player with the high bid
#  bid      - int    - the high bid
@app.route("/api/hand/gethighbid/", methods=["POST"])
def get_high_bid():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    hand_id = get_value_from_params(params, "hand_id")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Perform game-related logic
    high_bid_info = g_engines[game_id].get_high_bid(hand_id) 

    # Return the high bid
    data = high_bid_info
    return generate_return_string(data)


# Submit what trump your bid is in
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
#  trump    - string - suit that username picks to be trump. May be empty if just querying for trump
# Return (json data):
#  trump    - string - suit that was picked to be trump
@app.route("/api/hand/gettrump/", methods=["POST"])
def submit_and_get_trump():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")
    input_trump = get_value_from_params(params, "trump")
    query_only = False

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))
    if input_trump == None or len(input_trump) == 0:
        query_only = True

    # Perform game-related logic
    if not query_only:
        valid_trump = g_engines[game_id].submit_trump_for_player(username, input_trump) 
        if not valid_trump:
            return generate_error(9, "Invalid trump selected: {}".format(input_trump))
    trump = g_engines[game_id].get_trump() 

    # Return the high bid
    data = {}
    data["trump"] = trump
    return generate_return_string(data)


# Retrieve the information needed to play the next card
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  cards_played         - list of card_played - Cards that have been played so far, with username
#  current_winning_card - card          - The card that is currently winning the trick
#  lead_suit            - string        - The suit of the first card played
@app.route("/api/hand/getplayinginfo/", methods=["POST"])
def get_playing_info():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))


    # Perform game-related logic
    playing_info = g_engines[game_id].get_playing_info_for_player(username) 

    # Return the playing_info
    data = playing_info
    return generate_return_string(data)


# Choose which card to play
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
#  card - card - Card to play
# Return (json data):
#  current_trick        - list of cards - Cards that have been played so far, in order of play
#  current_winning_card - card          - The card that is currently winning the trick
#  lead_suit            - string        - The suit of the first card played
@app.route("/api/hand/submitcard/", methods=["POST"])
def submit_card_to_play():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")
    card = get_value_from_params(params, "card_to_play")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))
    if len(card.keys()) != 2 or "suit" not in card.keys() or "value" not in card.keys():
        return generate_error(7, "Improperly formatted card: {}".format(str(card)))

    # Perform game-related logic
    valid_card = g_engines[game_id].submit_card_to_play_for_player(username, card) 
    if not valid_card:
        return generate_error(8, "Unable to play {} of {}, please pick another card".format(card["value"], card["suit"]))

    # Return success
    return generate_return_string()


# Retrieve the results of the previous trick
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  winner        - string  - The winner of the trick
#  cards_played  - list of card_played objects  -  a card_played object is a username and a card
@app.route("/api/hand/gettrickresults/", methods=["POST"])
def get_trick_results():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in g_engines[game_id].get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))


    # Perform game-related logic
    trick_results = g_engines[game_id].get_trick_results_for_player(username) 

    # Return the playing_info
    data = trick_results
    return generate_return_string(data)


# Retrieve the results of the previous hand
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  hand_id  - string - ID of hand we want results for
# Return (json data):
#  high_winner  - string  - The winner of high
#  low_winner   - string  - The winner of low
#  jack_winner  - string  - The winner of jack
#  jick_winner  - string  - The winner of jick
#  game_winner  - string  - The winner of game
@app.route("/api/hand/getresults/", methods=["POST"])
def get_hand_results():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    hand_id = get_value_from_params(params, "hand_id")

    # Check input
    if game_id not in g_engines:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Perform game-related logic
    hand_results = g_engines[game_id].get_hand_results(hand_id)

    # Return the playing_info
    data = hand_results
    return generate_return_string(data)


