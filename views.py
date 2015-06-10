# __author__ = 'cory'
# from flask import request, redirect, render_template, url_for, flash, Blueprint
# from flask.ext.login import login_required, current_user
#
# from models import GameRoom, Player
# from cards_app import session, app
#
# from flask_login import LoginManager
# login_manager = LoginManager()
# login_manager.init_app(app)
#
# @login_manager.user_loader
# def load_user(player_id):
#     return Player.get(player_id)
#
#
# """
# Default login and logout views from Flask Tutorial
# these don't do anythng right now.
# how is session.pop() supposed to work?
# """
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('game_page'))
#     return render_template('login.html', error=error)
#
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))
#
#
# @app.route('/')
# def index():
#     return render_template('login.html')
#
# @app.route('/game_page')
# def game_page():
#     games = GameRoom.query.all()
#     return render_template('game_page.html')
#
#
# @app.route('/room/<int:room_id>')
# @login_required
# def blackjack_room(room_id):
#     context = {}
#     room = session.query(GameRoom).filter(GameRoom.id == room_id).all()[0]
#     game = GameRoom.game
#     players = []
#     for player in game.players:
#         player_dict = {'hands': player.hands, 'bank': player.bank,
#                        'name': player.username}
#     return render_template('blackjack_room.html', context=context)
#
#
# @app.route('/cards/bet/')
# @login_required
# def bet():
#     bet_value = request.form['betValue']
#     hand = request.form['hand_id']
#     bet(hand, bet_value)
#
# # @app.before_request
# # def check_turn(game_room):
# #     player = current_user
# #     if game_room.current_player != player:
# #         # return data to tell player he can't do this
# #         pass
# #     else:
# #         # If it's the player's turn pass, and allow action
# #         pass