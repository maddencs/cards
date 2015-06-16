from flask import Flask, request, redirect, render_template, url_for, flash, abort
from flask.ext.login import login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables
from models import GameRoom, Player, Game, LoginForm
import json
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager

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
    form = LoginForm()
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = session.query(Player).filter(Player.email == email).all()[0]
        if user and check_password_hash(user.password, password):
            user.authenticated = True
            login_user(user)
            flash('Logged in succesfully.', 'success')
            return redirect(next or url_for('game_page'))
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
    return render_template('game_page.html', games=game_rooms)

@app.route('/create_game/<string:game_type>', methods=['GET'])
def create_game(game_type):
    if request.method == 'GET':
        game = Game(game_type)
        session.add(game)
        session.flush()
        return redirect(url_for('game_room', game_id=game.id))

@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/room/<int:game_id>')
@login_required
def game_room(game_id, methods=['POST', 'GET']):
    context = {}
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    if game.type == 'Blackjack':
        if game.is_active:
            context['stats'] = game.stats
        return render_template('blackjack_room.html', context=context)

@app.route('/game_stats/<int:game_id>')
def game_stats(game_id):
    game = session.query(Game).filter(Game.id == game_id).all()[0]
    return json.dumps({'stats': game.stats}, indent=4, content_type='application/json')

@app.route('/cards/bet/')
@login_required
def bet():
    bet_value = request.form['betValue']
    hand = request.form['hand_id']
    bet(hand, bet_value)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        email = request.form['email']
        if len(session.query(Player).filter(Player.email == email).all()) < 1:
            password = generate_password_hash(request.form['password'], method='pbkdf2:sha1', salt_length=8)
            player = Player(email, password)
            session.add(player)
            session.commit()
            login_user(player)
            flash('Account created and logged in.', 'success')
            return redirect(url_for('game_page'))
        else:
            flash('That username is taken.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
