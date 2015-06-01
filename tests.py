import os
import cards_app
import unittest
import tempfile
import collections
from timeit import Timer
from models import Player, Game, Card, Hand, Turn
from lib import piece_maker, shuffle, hit, bet, split
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
        h.cards.extend(cards)
        cards_app.session.commit()
        # end of setup
        # deck is made in setUp() with piece_maker() ha
        deck = cards_app.session.query(Hand).filter(Hand.id == h.id).all()[0]
        player = p
        hand2 = cards_app.session.query(Hand).filter(Hand.player_id == player.id).all()[0]
        assert deck.cards != shuffle(deck)
        assert player.name == 'Cory'
        game = cards_app.session.query(Game).filter(Game.players.any(id=player.id)).all()
        hit(hand2, deck, 1)
        cards_app.session.commit()
        # do we still have 52 cards after hitting?
        assert len(set(deck.cards)) + len(set(hand2.cards)) == 52
        cards = cards_app.session.query(Card).filter(Card.player_id == p.id)
        for card in cards:
            cards_app.session.delete(card)
        cards_app.session.delete(p)
        cards_app.session.delete(g)
        cards_app.session.delete(h)
        cards_app.session.delete(hand2)
        cards_app.session.commit()

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

    def test_split(self):
        cards = [Card(sequence=1), Card(sequence=1)]
        hand = Hand()
        player = Player()
        game = Game('Blackjack')
        player.hands.append(hand)
        player.cards.extend(cards)
        game.hands.append(hand)
        hand.cards.extend(cards)
        split(hand)
        hands = player.hands
        cards = player.cards
        assert len(hands) == 2
        assert len(cards) == 2
        assert hands[0].cards[0].sequence == hands[1].cards[0].sequence

    def test_blackjack_player_wins(self):
        player = Player()
        cards_app.session.add(player)
        game = Game('Blackjack')
        hand = Hand()
        turn = Turn()
        player.turns.append(turn)
        game.turns.append(turn)
        player.hands.append(hand)
        game.hands.append(hand)
        game.players.append(player)

        cards_app.session.flush()
        bank_before_bet = player.bank
        bet(hand, 50)
        cards = [Card(sequence=1), Card(sequence=10)]
        hand.cards.extend(cards)
        count_blackjack(hand)
        blackjack(hand)
        cards_app.session.flush()
        # player wins with nautral blackjack
        assert player.bank == (bank_before_bet + 75)
        # player stands on 18, dealer stands on 17
        hand.cards = [Card(sequence=10), Card(sequence=8)]
        bet(hand, 50)
        game.dealer = Player()
        dealer = game.dealer
        dealer.cards = [Card(sequence=10), Card(sequence=17)]
        dealer_hand = Hand()
        dealer_hand.cards = dealer.cards
        # game.deal
        # figure out mixin with backref

    def test_blackjack_player_loses(self):
        game = Game('Blackjack')
        cards = [Card(sequence=10), Card(sequence=10), Card(sequence=10)]
        player = Player()
        cards_app.session.add(player)
        hand = Hand()
        player.hands.append(hand)
        game.players.append(player)
        game.hands.append(hand)
        cards_app.session.flush()
        hand.cards.extend(cards)
        bank_after_bet = player.bank
        count_blackjack(hand)
        blackjack(hand)
        # player loses if he breaks
        assert player.bank == bank_after_bet

        hand.cards = [Card(sequence=10), Card(sequence=5)]
        bet(hand, 50)



if __name__ == '__main__':
    unittest.main()
