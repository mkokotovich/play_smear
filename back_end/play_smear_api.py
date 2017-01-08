from flask import Flask, abort, request
import json

app = Flask(__name__)

global_game_id = 0
def generate_game_id():
    global global_game_id
    global_game_id += 1
    return str(global_game_id)


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


@app.route("/api/startgame/", methods=["POST"])
def start_game():
    # Read input
    params = get_params_or_abort(request)
    numPlayers = int(get_value_from_params(params, "numPlayers"))
    username = get_value_from_params(params, "username")

    # Perform game-related logic
    game_id = generate_game_id()
    app.logger.debug("Starting game {} with {} players using username: {}".format(game_id, numPlayers, username))
    # TODO: Start a smear game with numPlayer players, using username for the name of player0
    # TODO: Capture the names of other players
    other_players = []
    for i in range(1, numPlayers+1):
        other_players.append("player{}".format(i))

    # Return result
    ret = {}
    ret["game_id"] = game_id
    ret["other_players"] = other_players
    return json.dumps(ret)
