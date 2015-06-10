from flask import Flask, request, redirect, render_template, url_for, flash, abort
from flask.ext.login import login_required, login_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables
from models import GameRoom, Player, Game, LoginForm
import json
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
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = token.split(':')
        user_entry = session.query(Player).filter(Player.username == username)
        if (user_entry is not None):
            user = Player(user_entry[0], user_entry[1])

@login_manager.user_loader
def load_user(player_id):
    return Player.query.get(player_id)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session.logged_in = True
#             flash('You were logged in')
#             return redirect(url_for('game_page'))
#     return render_template('login.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate():
        print(form.username.data)
        user = session.query(Player).filter(Player.username == form.username.data).all()[0]
        login_user(user)
        flash('Logged in successfully')
        _next = request.args.get('next')
        if not next(_next):
            return abort(400)
        return redirect(next or url_for('game_page'))
    return render_template('login.html', form=form)

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
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/room/<int:game_id>')
@login_required
def game_room(game_id):
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

if __name__ == '__main__':
    app.run(debug=True)