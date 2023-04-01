from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# in-memory database to store game state
games = {}

@app.route('/game', methods=['POST'])
def new_game():
    # create a new game with a random player order
    players = request.json['players']
    random.shuffle(players)
    games[request.json['game_id']] = {'players': players, 'turn': 0, 'cards': []}
    return jsonify({'success': True})

@app.route('/game/<game_id>/play', methods=['POST'])
def play_card(game_id):
    # check if game exists
    if game_id not in games:
        return jsonify({'success': False, 'message': 'Game not found'})

    # check if it's the player's turn
    current_player = games[game_id]['players'][games[game_id]['turn']]
    if current_player != request.json['player']:
        return jsonify({'success': False, 'message': 'Not your turn'})

    # add the played card to the discard pile
    card = request.json['card']
    games[game_id]['cards'].append(card)

    # advance to the next player's turn
    games[game_id]['turn'] = (games[game_id]['turn'] + 1) % len(games[game_id]['players'])

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
