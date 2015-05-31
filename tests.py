import os
import cards_app
import unittest
import tempfile
import collections
from timeit import Timer
from models import Player, Game, Card, Hand, Turn
from lib import piece_maker, shuffle, hit, bet
from games import count_blackjack, blackjack
from sqlalchemy import and_

suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
card_values = ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']

class CardsTestCase(unittest.TestCase):
    def setUp(self):
        cards_app.app.self_fd, cards_app.app.config['DATABASE'] = tempfile.mkstemp()
        cards_app.app.config['TESTING'] = True
        self.app = cards_app.app.test_client()

    def tearDown(self):
        os.close(cards_app.app.self_fd)
        os.unlink(cards_app.app.config['DATABASE'])

    def test_make_deck_shuffle_hit(self):
        # setup
        p = Player()
        p.name = 'Cory'
        g = Game('BlackJack')
        g.players.append(p)
        h = Hand()
        h2 = Hand()
        g.hands.append(h)
        p.hands.append(h2)
        cards = piece_maker(suits, card_values, 1)
        for card in cards:
            cards_app.session.add(card)
        h.cards.extend(cards)
        cards_app.session.add(p)
        cards_app.session.add(g)
        cards_app.session.add(h)
        cards_app.session.add(h2)
        cards_app.session.commit()
        # end of setup
        # deck is made in setUp() with piece_maker() ha
        deck = cards_app.session.query(Hand).filter(Hand.id == h.id).all()[0]
        game = deck.game
        cards = deck.cards
        player = cards_app.session.query(Player).filter(Player.id == p.id)[0]
        cards2 = cards_app.session.query(Card).filter(Card.hand == deck).all()
        hand2 = cards_app.session.query(Hand).filter(Hand.player_id == player.id).all()[0]
        cards = shuffle(deck)
        assert deck.cards != shuffle(deck)
        assert player.name == 'Cory'
        game = cards_app.session.query(Game).filter(Game.players.any(id=player.id)).all()
        hand = cards_app.session.query(Player.hands).filter(Hand.player_id == player.id).filter(
            Hand.game_id == game[0].id).all()
        hit(hand2, deck, 1)
        cards_app.session.commit()
        assert len(set(deck.cards)) + len(set(hand2.cards)) == 52
        cards = cards_app.session.query(Card).filter(Card.player_id == p.id)
        for card in cards:
            cards_app.session.delete(card)
        cards_app.session.delete(p)
        cards_app.session.delete(g)
        cards_app.session.delete(h)
        cards_app.session.delete(hand2)
        cards_app.session.commit()
        # t = Timer(lambda: shuffle(deck))

    def test_count_blackjack_hand(self):
        hand = Hand()
        cards = [Card(sequence=1), Card(sequence=2), Card(sequence=11), Card(sequence=12)]
        hand.cards.append(cards[0])
        hand.cards.append(cards[2])
        count_blackjack(hand)
        assert hand.score == 21
        hand = Hand()
        hand.cards.extend(cards)
        count_blackjack(hand)
        assert hand.score == 23

    def test_blackjack_player_wins(self):
        player = Player()
        game = Game('Blackjack')
        hand = Hand()
        turn = Turn()
        # this isn't saving turn to player.turns for some reason
        player.turns.append(turn)
        game.turns.append(turn)
        player.hands.append(hand)
        game.hands.append(hand)
        game.players.add(player)
        cards = [Card(value=10), Card(sequence=1)]
        bank_before_bet = player.bank
        bet(player, hand, 50)
        # Getting an ace and a king from the deck, natural 21. payout 3:2
        cards = [Card(sequence=1), Card(sequence=10)]
        hand.cards.append(cards)
        blackjack(hand)
        assert game.is_over == True
        assert player.bank == (bank_before_bet + 125)
        # need to add stand wins, other blackjack wins

    def test_blackjack_player_loses(self):
        game = Game('Blackjack')
        cards = [Card(value=10), Card(value=10), Card(value=10)]
        player = Player()
        hand = Hand()
        player.hands.append(hand)
        game.players.append(player)
        game.hands.append(hand)
        hand.cards.extend(cards)
        blackjack(hand)
        # test not finished



if __name__ == '__main__':
    unittest.main()
