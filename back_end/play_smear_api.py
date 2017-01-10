from flask import Flask, abort, request
import json
import threading
from pysmear import smear_engine_api

app = Flask(__name__)

g_game_id = 0
g_game_id_lock = threading.Lock()
g_engines = {}


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
# Returns the game id
@app.route("/api/game/startstatus/<game_id>/", methods=["GET"])
def game_start_status(game_id):
    global g_engines
    player_names = []
    ret = {}
    ret["ready"] = g_engines[game_id].all_players_added()
    if ret["ready"]:
        player_names = g_engines[game_id].get_player_names()
    ret["player_names"] = player_names
    return json.dumps(ret)


# Starts a new game
# Returns the game id
@app.route("/api/game/start/", methods=["POST"])
def start_game():
    global g_engines
    # Read input
    params = get_params_or_abort(request)
    numPlayers = int(get_value_from_params(params, "numPlayers"))
    username = get_value_from_params(params, "username")

    # Perform game-related logic
    game_id = create_game_and_return_id()
    app.logger.debug("Starting game {} with {} players using username: {}".format(game_id, numPlayers, username))
    g_engines[game_id].create_new_game(num_players=numPlayers)
    g_engines[game_id].add_player(player_id=username, interactive=True)
    for i in range(1, numPlayers):
        new_player = "player{}".format(i)
        app.logger.debug("Adding player {} to game {}".format(new_player, game_id))
        g_engines[game_id].add_player(player_id=new_player, interactive=False)

    # Return result
    ret = {}
    ret["game_id"] = game_id
    return json.dumps(ret)
