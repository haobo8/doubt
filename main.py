from flask import Flask, jsonify, request
import random
import string
import time

app = Flask(__name__)

def generate_room_code(length=4):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

class Game:
    def __init__(self):
        self.deck = []
        self.players = []
        self.current_rank = None
        self.pile = []
        self.turn = 0

    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
        self.deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self, num_players):
        self.players = [[] for _ in range(num_players)]
        for i, card in enumerate(self.deck):
            self.players[i % num_players].append(card)

    def play_cards(self, player_idx, cards):
        for card in cards:
            self.players[player_idx].remove(card)
            self.pile.append(card)
        self.current_rank = cards[0]['rank']
        self.turn = (self.turn + 1) % len(self.players)

    def challenge(self, challenger_idx):
        if self.pile and self.pile[-1]['rank'] != self.current_rank:
            self.players[self.turn - 1].extend(self.pile)
            return False
        else:
            self.players[challenger_idx].extend(self.pile)
            return True

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

class Player:
    def __init__(self, name):
        self.name = name
        self.online = True

class Room:
    def __init__(self, code, host):
        self.code = code
        self.players = [host]
        self.host = host
        self.game = Game()
        self.created_at = time.time()

class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, player_name):
        player = Player(player_name)
        code = generate_room_code()
        while code in self.rooms:
            code = generate_room_code()
        room = Room(code, player)
        self.rooms[code] = room
        return room

    def join_room(self, code, player_name):
        if code in self.rooms and len(self.rooms[code].players) < 7:
            player = Player(player_name)
            self.rooms[code].players.append(player)
            return player
        return None

    def remove_empty_rooms(self):
        current_time = time.time()
        self.rooms = {code: room for code, room in self.rooms.items() if current_time - room.created_at < 4 * 3600 or len(room.players) > 0}

room_manager = RoomManager()

@app.route('/create_room', methods=['POST'])
def create_room():
    player_name = request.json['player_name']
    room = room_manager.create_room(player_name)
    return jsonify(status='success', room_code=room.code)

@app.route('/join_room', methods=['POST'])
def join_room():
    room_code = request.json['room_code']
    player_name = request.json['player_name']
    player = room_manager.join_room(room_code, player_name)
    if player:
        return jsonify(status='success')
    return jsonify(status='error', message='Room not found or is full.')

@app.route('/start', methods=['POST'])
def start_game():
    room_code = request.json['room_code']
    room = room_manager.rooms.get(room_code)
    if room:
        num_players = len(room.players)
        room.game.create_deck()
        room.game.shuffle_deck()
        room.game.deal_cards(num_players)
        return jsonify(status='success')
    return jsonify(status='error', message='Room not found.')

@app.route('/play', methods=['POST'])
def play_cards():
    room_code = request.json['room_code']
    player_idx = request.json['player_idx']
    cards = request.json['cards']
    room = room_manager.rooms.get(room_code)
    if room:
        room.game.play_cards(player_idx, cards)
        return jsonify(status='success', turn=room.game.turn)
    return jsonify(status='error', message='Room not found.')

@app.route('/challenge', methods=['POST'])
def challenge():
    room_code = request.json['room_code']
    challenger_idx = request.json['challenger_idx']
    room = room_manager.rooms.get(room_code)
    if room:
        result = room.game.challenge(challenger_idx)
        room.game.next_turn()
        return jsonify(status='success', result=result, turn=room.game.turn)
    return jsonify(status='error', message='Room not found.')

if __name__ == '__main__':
    app.run(debug=True)
