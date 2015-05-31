import os
import cards_app
import unittest
import tempfile
import collections
from timeit import Timer
from models import Player, Game, Card, Hand
from lib import piece_maker, shuffle, hit, bet
from games import blackjack
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
        # cards_app.session.delete()

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
        print(hand2.id)
        cards = shuffle(deck)
        assert deck.cards != shuffle(deck)
        # assert len(set(cards)) == 52
        assert player.name == 'Cory'
        game = cards_app.session.query(Game).filter(Game.players.any(id=player.id)).all()
        hand = cards_app.session.query(Player.hands).filter(Hand.player_id == player.id).filter(
            Hand.game_id == game[0].id).all()
        hit(hand2, deck, 1)
        cards_app.session.commit()
        # print('this', len(set(hand2.cards)) + len(set(deck.cards)))
        assert len(set(deck.cards)) + len(set(hand2.cards)) == 52
        t = Timer(lambda: shuffle(cards))
        cards = cards_app.session.query(Card).filter(Card.player_id == p.id)
        for card in cards:
            cards_app.session.delete(card)
        cards_app.session.delete(p)
        cards_app.session.delete(g)
        cards_app.session.delete(h)
        cards_app.session.delete(hand2)
        cards_app.session.commit()
        # print(t.timeit(number=1000))

        def test_count_blackjack_hand(self):
            # This probably doesn't really need a test
            pass

        def test_blackjack_player_wins(self):
            p = Player()
            game = Game('Blackjack')
            hand = Hand()
            p.hands.append(hand)
            g.hands.append(hand)
            cards = [Card(value=10), Card(sequence=1)]
            bank_before_bet = player.bank
            bet(player, hand, 50)
            # Getting an ace and a king from the deck, natural 21. payout 3:2
            # this is a silly way to do this
            cards = [x for x in cards if(card.sequence==1) and (card.category==1) or (card.sequence==13) and (card.category==1)]
            hand.append(cards)
            blackjack(player, game)
            assert game.is_over == True
            assert p.bank == (bank_before_bet + 125)
            # need to add stand wins, other blackjack wins

        def test_blackjack_player_loses(self):
            game = Game('Blackjack')
            cards = [Card(value=10), Card(value=10), Card(value=10)]
            hand = Hand()
            hand.cards.append(cards)
            blackjack(hand, game)



if __name__ == '__main__':
    unittest.main()
