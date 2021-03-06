from flask import Flask, abort, request, make_response
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import json
import threading
from collections import namedtuple
import Queue
import time
import sys
import os
import inspect
import cPickle as pickle
import random
import uuid
from datetime import datetime
import requests


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/pysmear")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/pydealer")
from pysmear.pysmear import smear_engine_api
from pysmear.pysmear import smear_exceptions
from dbqueries.bid_stats import BidStats
from dbqueries.game_stats import GameStats
from dbqueries.daily_status import DailyStatus

app = Flask(__name__)
app.secret_key = "top secret key"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
login_manager = LoginManager()
login_manager.init_app(app)


global g_game_id
global g_game_id_lock
global g_game_play_lock
global g_engines
global g_cleanup_thread
global g_cleanup_queue
global g_game_timeout

g_game_id = 0
g_game_id_lock = threading.Lock()
g_game_play_lock = threading.Lock()
g_engines = {}
g_cleanup_queue = Queue.Queue()
g_cleanup_thread = None
g_game_timeout = 36000

ALL_COMPUTER_NAMES = [
        "Francis",
        "Claude",
        "Ivan",
        "Marie",
        #"Queen Elizabeth",
        "Elliot",
        "Alex",
        "Maisie",
        "Barack",
        "Leif",
        "Hermione",
        "Harry",
        "Ron",
        "Hagrid",
]


###### User Auth section ######

class User():

    def __init__(self, email):
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email


# Validate a user's login. TODO, support https and passwords and such.
# Allows us to access logged in user via current_user
# Input (json data from post):
#  email - string - user's email address
# Return
#  success - boolean - true if successfully logged in
@app.route("/api/user/login/", methods=["POST"])
def user_login():
    # mongo is dead
    return generate_return_string({})


# Logs a user out
# Input (json data from post):
#  None
# Return
#  success - boolean - true if successfully logged out
@app.route("/api/user/logout/", methods=["POST"])
@login_required
def user_logout():
    logout_user()
    data = {}
    data["success"] = True
    return generate_return_string(data)

##############################


# Creates a new engine in a thread-safe manner
def create_engine(engineDebug):
    global g_engines
    global g_game_id_lock
    global g_game_id
    game_id = None
    with g_game_id_lock:
        g_game_id += 1
        game_id = str(g_game_id)
        engine = smear_engine_api.SmearEngineApi(debug=engineDebug)
        g_engines[game_id] = engine
        #pickle.dump( engine, open( "engine{}.p".format(game_id), "wb" ) )
    return game_id


# Gets the engine in a thread-safe manner
def load_engine(game_id):
    engine = None
    with g_game_id_lock:
        if game_id in g_engines:
            engine = g_engines[game_id]
        #filename = "engine{}.p".format(game_id)
        #if os.path.isfile(filename):
        #    with open(filename, "rb") as pfile:
        #        engine = pickle.load(pfile)
    return engine


# Updates the engine in a thread-safe manner
def update_engine(game_id, engine):
    pass
    #with open("engine{}.p".format(game_id), "wb") as pfile:
    #    pickle.dump(engine, pfile)


# Removes the engine in a thread-safe manner
def remove_engine(game_id):
    with g_game_id_lock:
        del g_engines[game_id]
        #os.remove("engine{}.p".format(game_id))


# Advances the game in a thread-safe manner
def continue_game(engine):
    with g_game_play_lock:
        engine.continue_game()


# Keep a reference to Queue.Empty so it isn't garabage collected before the cleanup thread function needs it
unused_empty = Queue.Empty

# Cleans up games after an expiration period, to release resources
def cleanup_thread_function(engine_queue, game_timeout):
    global g_engines

    print "+++Starting cleanup thread with game_timeout of {}".format(game_timeout)
    check_for_inactive_games_interval = 60
    Game = namedtuple("Game", ["game_id", "expiration"])
    active_games = []
    while True:
        # Accept new games, and every 60 seconds check if any are inactive
        try:
            game_id = engine_queue.get(timeout=check_for_inactive_games_interval)
            if game_id is None:
                for game in active_games:
                    app.logger.debug("+++Received empty game_id, quitting all games and exiting")
                    active_games.remove(game)
                    engine = load_engine(game.game_id)
                    if engine is not None:
                        engine.finish_game()
                        remove_engine(game.game_id)
                return
            expiration = int(time.time()) + game_timeout
            app.logger.debug("+++Cleanup thread received game_id {}, setting expiration for {}".format(game_id, expiration))
            game = Game(game_id, expiration)
            active_games.append(game)
        except Queue.Empty:
            #app.logger.debug("+++Cleanup thread looking for games with expiration < {}".format(time.time()))
            for game in active_games:
                if game.expiration < time.time():
                    # Game has reached the expiration time
                    app.logger.debug("+++Game {} has reached the expiration time ({}), quitting".format(game.game_id, game.expiration))
                    active_games.remove(game)
                    engine = load_engine(game.game_id)
                    if engine is not None:
                        engine.finish_game()
                        remove_engine(game.game_id)


def initialize(cleanup_thread, cleanup_queue, game_timeout):
    # Start cleanup thread
    if cleanup_thread is None:
        cleanup_thread = threading.Thread(target=cleanup_thread_function, args = ( cleanup_queue, game_timeout, ))
        cleanup_thread.daemon = True
        cleanup_thread.start()

    # Signal that app is initialized
    with open("/tmp/app-initialized", 'a'):
        os.utime("/tmp/app-initialized", None)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def generate_error(status_id, message, error_code=500):
    func = inspect.currentframe().f_back.f_code
    location_str = "{} in {}:{}".format(
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    )
    app.logger.error("Returning error from {}: {} ({})".format(location_str, message, status_id))
    status = {}
    status["status_id"] = status_id
    status["message"] = message
    ret = {}
    ret["status"] = status
    ret["error"] = message
    return json.dumps(ret), error_code


def generate_return_string(data=None):
    func = inspect.currentframe().f_back.f_code
    location_str = "{} in {}:{}".format(
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    )
    app.logger.debug("Returning success from {} with data: {}".format(location_str, json.dumps(data, indent=2, separators=(',', ': '))))
    status = {}
    status["status_id"] = 0
    ret = {}
    ret["status"] = status
    ret["data"] = data
    return json.dumps(ret)


def create_game_and_return_id(engineDebug):
    global g_cleanup_queue
    game_id = create_engine(engineDebug)
    g_cleanup_queue.put(game_id)
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


# Checks on the status of a game. Returns status 503 if the game is not ready
# Input (json data from post):
#  game_id    - String - ID of game to check on
#  username   - String - username to check for
# Return (json data):
#  ready        - String/bool  - If the game is ready to start (all players have joined)
#  num_players  - int     - the number of players in the game
#  player_names - list of strings  - a list of all players in the game (updated as more join)
#  team_id      - int    - if ready == True, ID of the team the player is on
@app.route("/api/game/startstatus/", methods=["POST"])
def game_start_status():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    player_names = []
    data = {}
    data["ready"] = engine.all_players_added() and engine.game_is_started()
    player_names = engine.get_player_names()

    data["num_players"] = engine.get_desired_number_of_players()
    data["player_names"] = player_names

    if data["ready"]:
        team_id = engine.get_team_id_for_player(username)
        data["team_id"] = team_id

    return generate_return_string(data)


# Set the teams
# Input (json data from post):
#  game_id    - String - ID of game to check on
#  player_team_list    - list of player-team objects 
# Return (json data):
@app.route("/api/game/setteams/", methods=["POST"])
def game_set_teams():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    player_team_list = get_value_from_params(params, "player_team_list")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    allowed_to_set = engine.game_setting_teams()
    if allowed_to_set:
        # Set team for each player
        for pt in player_team_list:
            app.logger.debug("Setting player {} to team id {}".format(pt["player"], pt["team_id"]))
            engine.change_player_team(pt["player"], pt["team_id"])
        engine.update_player_orders()

    # Update persistent engine
    update_engine(game_id, engine)

    return generate_return_string({})


# Starts a game, after everyone has joined and decided teams
# Input (json data from post):
#  game_id    - String - ID of game to check on
# Return (json data):
@app.route("/api/game/start/", methods=["POST"])
def game_start():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Start the game
    engine.start_game()

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    return generate_return_string({})


def add_user_to_game(engine, game_id, username):
    if engine.all_players_added():
        # Game is already full
        return generate_error(1, "Game {} is already full, contains {} players".format(game_id, engine.get_desired_number_of_players()))

    try:
        engine.add_player(username=username, interactive=True, email = current_user.get_id() if current_user.is_authenticated else None)
    except smear_exceptions.SmearUserHasSameName as e:
        return generate_error(20, "Could not add user to game {}, {}".format(game_id, e.strerror))
    return None

def add_computers_to_game_if_needed(engine, game_id):
    if engine.all_human_players_joined():
        # All humans are in, add the robots and start the game
        num_players = engine.get_desired_number_of_players()
        num_humans = engine.get_desired_number_of_human_players()
        num_computers_needed = num_players-num_humans
        computers = list(ALL_COMPUTER_NAMES)
        while num_computers_needed > 0:
            new_player = random.choice(computers)
            computers.remove(new_player)
            app.logger.debug("Adding player {} to game {}".format(new_player, game_id))
            try:
                engine.add_player(username=new_player, interactive=False)
                num_computers_needed -= 1
            except smear_exceptions.SmearUserHasSameName as e:
                app.logger.debug("Failed adding computer {} to game {}: {}. Trying the next computer name".format(new_player, game_id, e.strerror))


# join a game
# Input (json data from post):
#  game_id  - string - ID of game to join
#  username - string - username to use
# Return
#  game_id  - string - ID of game we just joined
#  username - string - username to use
#  num_teams - number - number of teams total 
#  points_to_play_to - int - points the game will go to

@app.route("/api/game/join/", methods=["POST"])
def join_game():
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id", abort_if_absent=False)
    username = get_value_from_params(params, "username", abort_if_absent=False)

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Perform game-related logic
    result = add_user_to_game(engine, game_id, username)
    if result is not None:
        return result
    add_computers_to_game_if_needed(engine, game_id)

    num_teams = engine.get_num_teams()
    points_to_play_to = engine.get_points_to_play_to()
    graph_prefix = engine.get_graph_prefix()

    # Update persistent engine
    update_engine(game_id, engine)

    # Return result
    data = {}
    data["game_id"] = game_id
    data["username"] = username
    data["num_teams"] = num_teams
    data["points_to_play_to"] = points_to_play_to
    data["graph_prefix"] = graph_prefix
    return generate_return_string(data)


# rejoin a game
# Input (json data from post):
#  game_id  - string - ID of game to join
#  username - string - username to use
# Return
#  game_id  - string - ID of game we just joined
#  username - string - username to use
#  team_id  - int    - ID of the team the player is on
#  num_teams - number - number of teams total 
#  points_to_play_to - int - points the game will go to
@app.route("/api/game/rejoin/", methods=["POST"])
def rejoin_game():
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id", abort_if_absent=False)
    username = get_value_from_params(params, "username", abort_if_absent=False)

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    team_id = engine.get_team_id_for_player(username)
    num_teams = engine.get_num_teams()
    points_to_play_to = engine.get_points_to_play_to()
    graph_prefix = engine.get_graph_prefix()

    # Update persistent engine
    update_engine(game_id, engine)

    # Return result
    data = {}
    data["game_id"] = game_id
    data["username"] = username
    data["team_id"] = team_id
    data["num_teams"] = num_teams
    data["points_to_play_to"] = points_to_play_to
    data["graph_prefix"] = graph_prefix
    return generate_return_string(data)


# creates a new game
# Input (json data from post):
#  numPlayers - Integer - number of players in the game
#  numHumanPlayers - Integer - number of human players expected to join game
#  pointsToPlayTo - Integer - points for the game to play to
#  numTeams - Integer - number of teams to play with
# Return (json data):
#  game_id    - String  - Id of the game to be used in future API calls
@app.route("/api/game/create/", methods=["POST"])
def create_game():
    # Read input
    params = get_params_or_abort(request)
    numPlayerInput = get_value_from_params(params, "numPlayers")
    numHumanPlayersInput = get_value_from_params(params, "numHumanPlayers")
    pointsToPlayToInput = get_value_from_params(params, "pointsToPlayTo")
    numTeamsInput = get_value_from_params(params, "numTeams")
    numPlayers = 0
    numHumanPlayers = 0
    pointsToPlayTo = 0
    numTeams = 0

    # Default to debug = True
    engineDebug = True
    debugValue = get_value_from_params(params, "engineDebug", abort_if_absent=False)
    if debugValue == False:
        engineDebug = False

    try:
        numPlayers = int(numPlayerInput)
        if numPlayers < 2 or numPlayers > 8:
            raise ValueError("Invalid number of players")
    except ValueError:
        return generate_error(3, "Invalid number of players {}, must be between 2 and 8".format(numPlayerInput))
    try:
        numHumanPlayers = int(numHumanPlayersInput)
        if numHumanPlayers > numPlayers:
            raise ValueError("Invalid number of human players")
    except ValueError:
        return generate_error(3, "Invalid number of human players {}, must be less than or equal to number of players ({})".format(numHumanPlayersInput, numPlayers))
    try:
        pointsToPlayTo = int(pointsToPlayToInput)
        if pointsToPlayTo < 1:
            raise ValueError("Invalid number of points to play to")
    except ValueError:
        return generate_error(3, "Invalid number of points to play to {}, must be greater than zero".format(pointsToPlayToInput))
    try:
        numTeams = int(numTeamsInput)
        if numTeams < 0 or numTeams == 1:
            raise ValueError("Invalid number of points to play to")
    except ValueError:
        return generate_error(3, "Invalid number of teams {}, must be greater than zero but not equal to 1".format(numTeamsInput))

    # Perform game-related logic
    game_id = create_game_and_return_id(engineDebug)
    app.logger.debug("Starting game {} with {} players".format(game_id, numPlayers))
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Unusual error occurred, could not find game that was just created {}".format(game_id))

    # Skip graphs if we're disabling debug logging (normally this is only for tests)
    if engineDebug:
        graph_prefix = uuid.uuid4().hex
        static_dir = os.path.dirname(os.path.realpath(__file__)) + "/static"
        engine.set_graph_details(static_dir, graph_prefix)

    # Create new game
    engine.create_new_game(num_players=numPlayers, num_human_players=numHumanPlayers, score_to_play_to=pointsToPlayTo, num_teams=numTeams)

    # Update persistent engine
    update_engine(game_id, engine)

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
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    cards = engine.get_hand_for_player(username) 
    if cards == None:
        return generate_error(13, "Cards for {} in game {} are not available".format(username, game_id), error_code=503)

    hand_id = engine.get_hand_id() 

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

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
#  all_bids             - List of bids that have been submitted so far
#  dealer               - string        - Name of dealer
#  ready_to_play        - boolean       - Indicates if the game is ready for the user to subit his/her bid
#  force_two            - boolean       - Indicates if the bidder will have to bid two or take a set
#  current_bid          - int           - Current high bid
#  bidder               - string        - Current name of high bidder
@app.route("/api/hand/getbidinfo/", methods=["POST"])
def get_bid_info():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    bid_info = engine.get_bid_info_for_player(username) 
    if bid_info == None:
        bid_info = {}
        bid_info["all_bids"] = engine.get_bids_submitted_so_far()
        bid_info["ready"] = False
    else:
        bid_info["ready"] = True
    bid_info["dealer"] = engine.get_dealer()
    bid_info["waiting_for"] = engine.get_player_who_we_are_waiting_for(bidding=True)

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

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
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    valid_bid = engine.submit_bid_for_player(username, bid) 
    if not valid_bid:
        return generate_error(6, "Invalid bid ({}) for {}, unable to submit bid".format(bid, username))

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    # Return success
    return generate_return_string()


# Find out who the high bidder is, and what the bid is (not including trump, though)
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  hand_id  - string - ID of hand we're playing
# Return (json data):
#  all_bids             - List of bids that have been submitted so far
#  dealer               - string        - Name of dealer
#  ready_to_play        - boolean       - Indicates if the game is ready for the user to subit his/her bid
#  force_two            - boolean       - Indicates if the bidder will have to bid two or take a set
#  current_bid          - int           - Current high bid
#  bidder               - string        - Current name of high bidder
@app.route("/api/hand/gethighbid/", methods=["POST"])
def get_high_bid():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    hand_id_input = get_value_from_params(params, "hand_id")
    hand_id = 0
    try:
        hand_id = int(hand_id_input)
        if hand_id < 0:
            raise ValueError("Invalid hand_id")
    except ValueError:
        return generate_error(11, "Invalid hand_id ({})".format(hand_id_input))

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    high_bid_info = engine.get_high_bid(hand_id) 
    if high_bid_info == None:
        high_bid_info = {}
        high_bid_info["all_bids"] = engine.get_bids_submitted_so_far()
        high_bid_info["ready"] = False
    else:
        high_bid_info["ready"] = True
    high_bid_info["waiting_for"] = engine.get_player_who_we_are_waiting_for(bidding=True)

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

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
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")
    input_trump = get_value_from_params(params, "trump")
    query_only = False

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))
    if input_trump == None or len(input_trump) == 0:
        query_only = True

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    if not query_only:
        valid_trump = engine.submit_trump_for_player(username, input_trump) 
        if not valid_trump:
            return generate_error(9, "Invalid trump selected: {}".format(input_trump))

    # Continue the game play so trump is set
    continue_game(engine)

    # Perform game-related logic
    trump = engine.get_trump() 
    if trump == None:
        return generate_error(16, "trump for {} in game {} is not available".format(username, game_id), error_code=503)

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    # Return trump
    data = {}
    data["trump"] = trump
    return generate_return_string(data)


# Retrieve the information needed to play the next card
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  cards_played         - list of card_played - Cards that have been played so far, with username
#  ready_to_play        - boolean       - Indicates if the game is ready for the user to take his turn
#  current_winning_card - card          - The card that is currently winning the trick
#  lead_suit            - string        - The suit of the first card played
@app.route("/api/hand/getplayinginfo/", methods=["POST"])
def get_playing_info():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))


    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    playing_info = engine.get_playing_info_for_player(username) 
    if playing_info == None:
        playing_info = {}
        playing_info["cards_played"] = engine.get_cards_played_so_far()
        playing_info["ready_to_play"] = False
    else:
        playing_info["ready_to_play"] = True
    playing_info["waiting_for"] = engine.get_player_who_we_are_waiting_for(bidding=False)

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

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
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")
    card = get_value_from_params(params, "card_to_play")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))
    if len(card.keys()) != 2 or "suit" not in card.keys() or "value" not in card.keys():
        return generate_error(7, "Improperly formatted card: {}".format(str(card)))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    valid_card = engine.submit_card_to_play_for_player(username, card) 
    if not valid_card:
        return generate_error(8, "Unable to play {} of {}, please pick another card".format(card["value"], card["suit"]))

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    # Return success
    return generate_return_string()


# Retrieve the results of the previous trick
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  cards_played   - list of card_played objects  -  a card_played object is a username and a card
#  trick_finished - boolean  - The trick is finished, no need to call this again
#  winner         - string   - The winner of the trick
@app.route("/api/hand/gettrickresults/", methods=["POST"])
def get_trick_results():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))


    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    trick_results = engine.get_trick_results_for_player(username) 
    if trick_results == None:
        trick_results = {}
        trick_results["cards_played"] = engine.get_cards_played_so_far()
        trick_results["trick_finished"] = False
    else:
        trick_results["trick_finished"] = True
    trick_results["waiting_for"] = engine.get_player_who_we_are_waiting_for(bidding=False)

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    # Return the playing_info
    data = trick_results
    return generate_return_string(data)


# Retrieve the results of the previous hand
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  hand_id  - int - ID of hand we want results for
# Return (json data):
#  high_winner  - string  - The winner of high
#  low_winner   - string  - The winner of low
#  jack_winner  - string  - The winner of jack
#  jick_winner  - string  - The winner of jick
#  game_winner  - string  - The winner of game
#  is_game_over - boolean - True if the game is now over
#  overall_winner - string - If is_game_over is True, set to the player who won the game
#  bidder_set   - boolean - True if the bidder was set
#  player_infos - array of player_info  - Updated names and scores for all players
@app.route("/api/hand/getresults/", methods=["POST"])
def get_hand_results():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    hand_id_input = get_value_from_params(params, "hand_id")
    hand_id = 0
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    try:
        hand_id = int(hand_id_input)
        if hand_id < 0:
            raise ValueError("Invalid hand_id")
    except ValueError:
        return generate_error(11, "Invalid hand_id ({})".format(hand_id_input))

    # Continue the game play
    continue_game(engine)

    # Perform game-related logic
    hand_results = engine.get_hand_results(hand_id)
    if hand_results == None:
        return generate_error(19, "hand results for hand {} in game {} are not available".format(hand_id, game_id), error_code=503)
    if hand_results["is_game_over"]:
        ready_to_delete = engine.player_is_finished(username)
        if ready_to_delete:
            app.logger.debug("Game {} is finished, removing engine".format(game_id))
            engine.finish_game()
            with g_game_id_lock:
                del g_engines[game_id]

    # Continue the game play
    continue_game(engine)

    # Update persistent engine
    update_engine(game_id, engine)

    # Return the playing_info
    data = hand_results
    return generate_return_string(data)


# Retrieve stats about a player
# Input (json data from post):
# Return (json data):
# List of key-value pairs, description and value
#
@app.route("/api/user/stats/", methods=["POST"])
@login_required
def get_stats_for_user():
    # Use current_user.get_id for the email
    # Get game stats
    game_stats = GameStats()
    game_stat_results = game_stats.get_stats_for_email(current_user.get_id())
    # Get bid stats
    bid_stats = BidStats()
    bid_stat_results = bid_stats.get_stats_for_email(current_user.get_id())

    # Return the playing_info
    all_stats = game_stat_results + bid_stat_results
    data = { "stats": all_stats }
    return generate_return_string(data)


# Helper functions for contact api
def load_mailgun_key():
    auth_key = None
    if "MAILGUN_KEY" in os.environ:
        auth_key = os.environ["MAILGUN_KEY"]
    if not auth_key:
        app.logger.error("Could not find MAILGUN_KEY environmental variable")
    return auth_key


def send_feedback_email(user_email, subject, body):
    auth_key = load_mailgun_key()
    if not auth_key:
        return False
    full_body = "Feedback received from {} on {}\n\n".format(user_email, datetime.now().strftime("%x"))
    full_body += "Subject: {}\n".format(subject)
    full_body += "Message: {}\n".format(body)
    r = requests.post(
        "https://api.mailgun.net/v3/mg.playsmear.com/messages",
        auth=("api", auth_key),
        data={"from": "Play Smear Feedback <feedback@playsmear.com>",
              "to": ["mkokotovich+smearfeedback@gmail.com"],
              "subject": "Play Smear Feedback: {}".format(subject),
              "text": full_body,
              "html": "<html><pre>{}</pre><br><br><br><a href='www.playsmear.com'>Unsubscribe</a></html>".format(full_body)})
    if r.status_code != 200:
        app.logger.error("Failed to send feedback email: {}".format(r.text))
        return False
    return True


def send_status_message(num_games, status):
    auth_key = load_mailgun_key()
    if not auth_key:
        return False
    r = requests.post(
        "https://api.mailgun.net/v3/mg.playsmear.com/messages",
        auth=("api", auth_key),
        data={"from": "Play Smear <admin@playsmear.com>",
              "to": ["mkokotovich@gmail.com"],
              "subject": "{} Games - Play Smear Daily Status for {}".format(num_games, datetime.now().strftime("%x")),
              "text": status,
              "html": "<html><pre>{}</pre><br><br><br><a href='www.playsmear.com'>Unsubscribe</a></html>".format(status)})
    if r.status_code != 200:
        app.logger.error("Failed to send status email: {}".format(r.text))
        return False
    return True


# Sends an email with feedback from the user
# Input (json data from post):
#  email
#  subject
#  body
# Return (json data):
#  Nothing, just status
#
@app.route("/api/feedback/", methods=["POST"])
def submit_feedback():
    # Read input
    params = get_params_or_abort(request)
    email = get_value_from_params(params, "email")
    subject = get_value_from_params(params, "subject")
    body = get_value_from_params(params, "body")

    if send_feedback_email(email, subject, body):
        return generate_return_string()
    else:
        return generate_error(20, "Unable to submit feedback now, try again later")


# Sends an email with daily status
# Input (json data from post):
#  None
# Return (json data):
#  Nothing, just status
#
@app.route("/api/status/", methods=["POST", "GET"])
def send_daily_status():
    daily_status = DailyStatus()
    daily_status.load_stats_since_previous_date(1)
    stats = daily_status.print_game_stats()
    num_games = daily_status.get_num_games()

    if send_status_message(num_games, stats):
        return generate_return_string()
    else:
        return generate_error(20, "Unable to send status email now, try again later")



# Returns a hint for which card a player should play
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  card
#
@app.route("/api/hand/hint/", methods=["POST"])
def get_hint_for_player():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Perform game-related logic
    card_to_play = engine.get_hint_for_player(username) 
    if card_to_play == None:
        return generate_error(21, "Unable to get hint for {}".format(username))

    # Return the playing_info
    return generate_return_string(card_to_play)


# Returns a hint for what bid a player should make
# Input (json data from post):
#  game_id  - string - ID of game we're playing
#  username - string - username of player
# Return (json data):
#  bid
#  trump
#
@app.route("/api/hand/bidhint/", methods=["POST"])
def get_bid_hint_for_player():
    # Read input
    params = get_params_or_abort(request)
    game_id = get_value_from_params(params, "game_id")
    username = get_value_from_params(params, "username")

    # Check input
    engine = load_engine(game_id)
    if engine is None:
        return generate_error(4, "Could not find game {}".format(game_id))
    if username not in engine.get_player_names():
        return generate_error(5, "Could not find user {} in game {}".format(username, game_id))

    # Perform game-related logic
    bid_hint = engine.get_bid_hint_for_player(username) 
    if bid_hint == None:
        return generate_error(22, "Unable to get bid hint for {}".format(username))

    # Return the playing_info
    return generate_return_string(bid_hint)



initialize(g_cleanup_thread, g_cleanup_queue, g_game_timeout)

if __name__ == '__main__':

    my_host = "0.0.0.0"
    my_port = 5000
    app.debug = True
    app.run(threaded=True, host=my_host, port=my_port)

