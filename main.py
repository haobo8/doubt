from flask import Flask, render_template, session, request
import random

app = Flask(__name__)
app.secret_key = "setitaskawarage1879"

suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
ranks = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']

def new_deck():
    deck = [(rank, suit) for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

rooms = {}
num_rooms = 0
room_numbers = {}

@app.route("/")
def index():
    
    if "room" not in session:
        session["room"] = 1

    if session["room"] not in rooms:
        rooms[session["room"]] = [new_deck(), [], []]

    if "player" not in session:
        player = 1
        session["player"] = player
        rooms[session["room"]][1].append(player)
        rooms[session["room"]][2].append([rooms[session["room"]][0].pop() for i in range(2)])
    else:
        player = session["player"]

    deck, players, hands = rooms[session["room"]]
    hand = hands[players.index(player)]
    points = total_points(hand)

    if request.args.get("hit"):
        hand.append(deck.pop())
        points = total_points(hand)
        if points > 21:
            return render_template("lose.html")

    return render_template("start.html", hand=hand, points=points)

@app.route("/room/<room_number>")
def room(room_number):
    if "room" not in session:
        return "Error: Room not found in session"

    if "player" not in session:
        return "Error: Player not found in session"

    player = session["player"]
    room = session["room"]
    deck, players, hands = rooms[room]
    my_hand = hands[players.index(player)]
    my_points = total_points(my_hand)

    dealer_hand = hands[-1]
    while total_points(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    dealer_points = total_points(dealer_hand)

    if my_points > 21:
        return render_template("lose.html")
    elif dealer_points > 21:
        return render_template("win.html")
    elif my_points > dealer_points:
        return render_template("win.html")
    else:
        return render_template("lose.html")
