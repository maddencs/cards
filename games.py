from models import *
from cards_app import session

def blackjack(hand, game):
    players = game.players
    deck = game.deck
    turn = game.turn
    for player in players:
        player_turn = session.query(Turn).filter(Turn.player_id==player.id)\
            .filter(Turn.game_id==game.id)