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


def generate_return_string(data):
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
    # cards = g_engines[game_id].get_next_deal() 

    # Return result
    data = {}
    #data["cards"] = cards
    return generate_return_string(data)

