from flask import Flask, request, redirect, render_template, url_for, flash, abort, jsonify
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables
from models import Player, Game, LoginForm, Hand, Seat, GameRoom
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager
from lib_dir.card_actions import hit, piece_maker, split, bet
from blackjack.rules import count_blackjack, evaluate_hit
import datetime

suits = ['Spade', 'Heart', 'Diamond', 'Club']
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
        if user_entry is not None:
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
    game_rooms = session.query(GameRoom)
    return render_template('game_page.html', rooms=game_rooms)


@app.route('/create_game/<string:game_type>/<int:room_id>', methods=['GET'])
def create_game(game_type, room_id):
    if request.method == 'GET':
        dealer = Player()
        session.add(dealer)
        game = Game(game_type)
        session.add(game)
        deck = Hand()
        session.add(deck)
        game.deck = deck
        if game_type == 'Blackjack':
            i = 1
            while i <= 5:
                seat = Seat(i)
                game.seats.append(seat)
                session.commit()
                i += 1
        game.time = datetime.datetime.now()
        game.dealer = dealer
        dealer_hand = Hand()
        dealer.hands.append(dealer_hand)
        game.players.append(current_user)
        session.commit()
        if room_id != 0:
            room = session.query(GameRoom).filter(GameRoom.id == room_id).all()[0]
            room.current_game = game
            return redirect(url_for('game_room', room_id=room_id))
        else:
            room = GameRoom()
            room.current_game = game
            session.commit()
            return redirect(url_for('game_room', room_id=room.id))


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/room/<int:room_id>', methods=['POST', 'GET'])
@login_required
def game_room(room_id):
    context = {}
    room = session.query(GameRoom).filter(GameRoom.id == room_id).all()[0]
    context['game'] = room.current_game
    if room.current_game.type == 'Blackjack':
        return render_template('blackjack_room.html', game=room.current_game)


@app.route('/bet/<int:hand_id>/<int:bet_value>', methods=['POST', 'GET'])
@login_required
def game_bet(hand_id, bet_value):
    data = {}
    hand = session.query(Hand).filter(Hand.id == hand_id).all()[0]
    if hand.player.bank >= bet_value:
        print('before')
        bet(hand, bet_value)
        print('after')
        session.commit()
        data['status'] = 'success'
    else:
        data['status'] = 'failed'
    seat = session.query(Seat).filter(Seat.game_id == hand.game_id).filter(Seat.player == current_user).all()[0]
    seat.time = datetime.datetime.utcnow()
    seat.ready = True
    session.commit()
    return jsonify(data)


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
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    if len(game.deck.cards) == 0:
        cards = piece_maker(suits, card_values, 1)
        session.add_all(cards)
        game.deck.cards = cards
    for seat in game.seats:
        if seat.player:
            hand = session.query(Hand).filter(Hand.game_id == game.id).filter(Hand.player_id == seat.player.pid).all()[0]
            if hand.bet != 0:
                hit(hand, 2)
                count_blackjack(hand)

    session.commit()
    game.time = datetime.datetime.utcnow()
    return jsonify({'status': 'done'})


@app.route('/game_stats/<int:game_id>', methods=['POST', 'GET'])
def game_stats(game_id):
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    stats = game.stats
    t_delta = abs(datetime.datetime.utcnow() - game.time).seconds
    if t_delta > 20:
        game.active = True
        game.time = datetime.datetime.utcnow()
    stats['time_delta'] = t_delta
    return jsonify(stats)


@app.route('/seat/<int:seat_id>', methods=['POST', 'GET'])
def sit(seat_id):
    if request.method == 'POST':
        seat = session.query(Seat).filter(Seat.id == seat_id).all()[0]
        current_user.seats.append(seat)
        seat.time = datetime.datetime.utcnow()
        game = session.query(Game).filter(Game.id == seat.game_id).all()[0]
        game.time = datetime.datetime.utcnow()
        game.players.append(current_user)
        hand = Hand()
        player = session.query(Player).filter(Player.pid == current_user.pid).all()[0]
        player.hands.append(hand)
        player.seats.append(seat)
        game.hands.append(hand)
        seat.game = game
        session.add(hand)
        session.commit()
        return jsonify(game.stats)
    else:
        seat = session.query(Seat).filter(Seat.game_id == seat_id).all()[0]
        return jsonify(seat.details)


@app.route('/status_check/<int:game_id>', methods=['POST', 'GET'])
def status_check(game_id):
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    date = request.form['date']
    date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
    delta = abs(date - game.time)
    # end user's turn by setting seat inactive if time since last move > 10 seconds
    # set current turn
    if delta.seconds > 10:
        for seat in game.seats:
            if seat.player is not None:
                if seat.ready and game.active:
                    game.current_turn = seat.seat_number
                    game.time = datetime.datetime.utcnow()
                    break
        session.commit()
    return jsonify(game.stats)


@app.route('/ready/seat/<int:seat_id>')
def ready_seat(seat_id):
    seat = session.query(Seat).filter(Seat.id == seat_id).all()[0]
    game = seat.game
    game.time = datetime.datetime.utcnow()
    seat.ready = True
    return jsonify({'status': 'success'})


@app.route('/split/hand/<int:hand_id>', methods=['POST', 'GET'])
def split(hand_id):
    hand = session.query(Hand).filter(Hand.id == hand_id).all()[0]
    player = hand.player
    game = hand.game
    new_hand = Hand()
    count_blackjack(hand)
    session.add(new_hand)
    new_hand.cards = [hand.cards.pop()]
    game.hands.append(new_hand)
    player.hands.append(new_hand)
    new_hand.cards.append(game.deck.cards.pop())
    hand.cards.append(game.deck.cards.pop())
    session.commit()
    return jsonify({'status': 'success'})


@app.route('/stand/hand/<int:hand_id>', methods=['POST', 'GET'])
def stand(hand_id):
    hand = session.query(Hand).filter(Hand.id == hand_id).all()[0]
    hand.is_turn = False
    hand.is_expired = True
    session.commit()
    return jsonify({'status': 'success'})


@app.route('/hit/hand/<int:hand_id>/<int:count>', methods=['POST', 'GET'])
def game_hit(hand_id, count):
    hand = session.query(Hand).filter(Hand.id == hand_id).all()[0]
    hit(hand, count)
    count_blackjack(hand)
    evaluate_hit(hand)
    session.commit()
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
