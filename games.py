from models import Hand, Turn, Game, Card, Player
from cards_app import session
from sqlalchemy.inspection import inspect

def count_blackjack(hand):
    hand.score = 0
    aces = []
    for card in hand.cards:
        if 2 <= card.sequence <= 10:
            hand.score += card.sequence
        elif card.sequence > 10:
            hand.score += 10
        else:
            aces.append(card)
    for ace in aces:
        if hand.score > 11:
            hand.score += 1
        else:
            hand.score += 11


def blackjack(hand):
    game = hand.game
    player = hand.player
    turn = session.query(Turn).filter(Turn.game == game).filter(Turn.player == player).all()
    if hand.score > 21:
        # go to next hand
        pass
    elif hand.score == 21:
        if len(hand.cards) == 2:
            player.bank += hand.bet * 2.5
            hand.bet = 0
        else:
            player.bank += hand.bet * 2
    elif len(hand.cards) == 5:
        # look into this blackjack rule
        pass
