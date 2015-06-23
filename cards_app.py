from flask import Flask, request, redirect, render_template, url_for, flash, abort, jsonify
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables
from models import Player, Game, LoginForm, Hand, Seat
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager
from lib_dir.card_actions import hit, piece_maker

suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
card_values = ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
app.secret_key = 'dev_password'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.request_loader
def load_user_from_request(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        email, password = token.split(':')
        user_entry = session.query(Player).filter(Player.email == email)
        if (user_entry is not None):
            user = Player(user_entry[0], user_entry[1])

@login_manager.user_loader
def load_user(email):
    if len(session.query(Player).filter(Player.email == email).all()) != 0:
        return session.query(Player).filter(Player.email == email).all()[0]

@app.route('/login', methods=['GET', 'POST'])
def login():
    # form = LoginForm()
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = session.query(Player).filter(Player.email == email).all()[0]
        if user and check_password_hash(user.password, password):
            user.authenticated = True
            login_user(user)
            flash('Logged in succesfully.', 'success')
            return redirect(url_for('game_page'))
        else:
            flash('Incorrect username or password', 'danger')
            return redirect(url_for('login'))

    if current_user.is_anonymous():
        return render_template('login.html')
    else:
        return redirect(url_for('index'))

@app.route('/game_page', methods=['GET', 'POST'])
def game_page():
    game_rooms = session.query(Game)
    return render_template('game_page.html', games=game_rooms)

@app.route('/create_game/<string:game_type>', methods=['GET'])
def create_game(game_type):
    if request.method == 'GET':
        dealer = Player()
        game = Game(game_type)
        if game_type == 'Blackjack':
            i = 1
            while i <= 5:
                seat = Seat(i)
                game.seats.append(seat)
                i += 1
        game.dealer = dealer
        dealer_hand = Hand()
        dealer.hands.append(dealer_hand)
        game.players.append(current_user)
        session.add(game)
        session.commit()
        return redirect(url_for('game_room', game_id=game.id))

@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/room/<int:game_id>', methods=['POST', 'GET'])
@login_required
def game_room(game_id):
    context = {}
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    context['game'] = game
    if game.type == 'Blackjack':
        return render_template('blackjack_room.html', game=game)

@app.route('/bet/')
@login_required
def bet():
    bet_value = request.form['betValue']
    hand = session.query(Hand).filter(Hand.id == request.form['hand_id']).all()[0]
    bet(hand, bet_value)
    session.commit()

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        if len(session.query(Player).filter(Player.username == username).all()) < 1:
            password = generate_password_hash(request.form['password'], method='pbkdf2:sha1', salt_length=8)
            player = Player()
            player.email = email
            player.username = username
            player.password = password
            player.authenticated = True
            session.add(player)
            session.commit()
            login_user(player)
            flash('Account created and logged in.', 'success')
            return redirect(url_for('game_page'))
        else:
            flash('That username is taken.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/blackjack_deal/<int:game_id>', methods=['POST', 'GET'])
def blackjack_deal(game_id):
    deck = Hand()
    deck.cards = piece_maker(suits, card_values, 1)
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    game.deck = deck
    game.is_active = True
    game.is_over = False
    for seat in game.seats:
        if seat.player is not None:
            game.current_turn = seat.seat_number
            session.commit()
    for player in game.players:
        if session.query(Seat).filter(Seat.player == player).filter(Seat.game_id == game_id).all():
            hand = session.query(Hand).filter(Hand.player_id == player.pid).filter(Hand.game_id == game_id).all()[0]
            hit(hand, 2)
            session.commit()
    return jsonify({'status': 'done'})

@app.route('/game_stats/<int:game_id>', methods=['POST', 'GET'])
def game_stats(game_id):
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    return jsonify(game.stats)

@app.route('/game/<int:game_id>/seat/<int:seat_number>', methods=['POST', 'GET'])
def sit(game_id, seat_number):
    if request.method == 'POST':
        seat = session.query(Seat).filter(Seat.game_id == game_id).filter(Seat.seat_number == seat_number).all()[0]
        seat.player = current_user
        game = session.query(Game).filter(Game.id == game_id).all()[0]
        game.players.append(current_user)
        game.seats.append(seat)
        hand = Hand()
        current_user.hands.append(hand)
        game.hands.append(hand)
        session.commit()
    else:
        seat = session.query(Seat).filter(Seat.seat_number == seat_number).filter(Seat.game_id == game_id).all()[0]
        return jsonify(seat.details)

@app.route('/status_check/<int:game_id>', methods=['POST', 'GET'])
def status_check(game_id):
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    current_seats = []
    for seat in game.seats:
        if seat.player is not None:
            current_seats.append(seat)

    players = game.players



if __name__ == '__main__':
    app.run(debug=True)

