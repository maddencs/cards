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
        i += 1
    return result


# make this more efficient?
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


def hit(hand, source, count):
    cards = source.cards
    player = hand.player
    i = 0
    while i < count:
        card = cards.pop()
        card.player_id = player.id
        hand.cards.append(card)
        i += 1
    session.commit()


def bet(hand, points):
    hand.bet += points


def split(hand):
    player = session.query(Player).filter(Player.id == hand.player_id).all()[0]
    game = session.query(Game).filter(Game.id == hand.game_id).all()[0]
    card = hand.cards.pop()
    new_hand = Hand()
    player.hands.append(new_hand)
    game.hands.append(new_hand)
