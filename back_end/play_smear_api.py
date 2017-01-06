from flask import Flask
import json

app = Flask(__name__)

def generate_game_id():
    return "abcd"

@app.route('/api/startgame/<int:numPlayers>')
def start_game(numPlayers):
    ret = {}
    game_id = generate_game_id()
    app.logger.debug('Starting game {} with {} players'.format(game_id, numPlayers))
    ret["game_id"] = game_id
    return json.dumps(ret)
