__author__ = 'cory'
from models import Player, Game, Card, Hand
from random import randint
from cards_app import session


def piece_maker(category, values, decks):
    i = 0
    result = []
    while i < decks:
        for c in category:
            for v in values:
                p = Card(category=c, sequence=(values.index(v) + 1), value=v)
                result.append(p)
                session.add(p)
        i += 1
    return result

def shuffle(deck):
    cards = deck.cards
    i = 0
    cards_left = len(cards)
    cards_left_index = (cards_left - 1)
    random_int = randint(0, cards_left_index)
    result = []
    while i < 7:
        while cards_left:
            if cards[random_int] not in result:
                result.append(cards[random_int])
                cards = [x for x in cards if x not in result]
                cards_left = len(cards)
                cards_left_index = (cards_left - 1)

                if cards_left:
                    random_int = randint(0, cards_left_index)
        i += 1
    return result

def hit(hand, count):
    cards = hand.game.deck.cards
    player = hand.player
    i = 0
    while i < count:
        card = cards.pop()
        player.cards.append(card)
        hand.cards.append(card)
        i += 1
    session.commit()

def bet(hand, points):
    hand.player.bank -= points
    hand.bet += points
    session.commit()

def split(hand):
    player = hand.player
    game = hand.game
    new_hand = Hand()
    new_hand.cards = [hand.cards.pop()]
    game.hands.append(new_hand)
    player.hands.append(new_hand)
    new_hand.cards.append(game.deck.cards.pop())
    hand.cards.append(game.deck.cards.pop())
    session.flush()
