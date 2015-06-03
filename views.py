__author__ = 'cory'
from models import Player, Game, Hand, Turn, Card, GameRoom
from cards_app import session, app
from flask import request, redirect, render_template, url_for, flash



"""
Default login and logout views from Flask Tutorial
these don't do anythng right now.
how is session.pop() supposed to work?
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/')
def index():
    """
    show game index page, this is where the user will choose the game type
    choosing a type will show available games in that category
    :return:
    """
    pass

@app.route('/room/<int:room_id>')
def game_room(room_id):
    context = {}
    room = session.query(GameRoom).filter(GameRoom.id==room_id).all()[0]
    game = GameRoom.game
    players = []
    for player in game.players:
        player_dict = {'hands':player.hands, 'bank':player.bank,
                       'name': player.username}
    return render_template('game_room.html', context)
