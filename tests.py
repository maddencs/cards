import os
import cards_app
import unittest
import tempfile
from models import Player, Game, Card, Hand, Turn
from lib import piece_maker, shuffle, hit, bet, split
from games import count_blackjack, evaluate_hit, blackjack_dealer, blackjack_payout

suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
card_values = ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']
player = Player()
game = Game('BlackJack')
hand = Hand()

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
        turn = Turn()
        player.first_name = 'Cory'
        player.last_name = 'Madden'
        assert player.fullname == 'Cory Madden'
        game.players.append(player)
        h = Hand()
        h2 = Hand()
        game.hands.append(h)
        player.hands.append(h2)
        cards = piece_maker(suits, card_values, 1)
        h.cards.extend(cards)
        cards_app.session.commit()
        # end of setup
        # deck is made in setUp() with piece_maker() ha
        game.deck = h
        game.hands.append(h2)
        deck = game.deck
        hand2 = h2
        cards_app.session.flush()
        assert deck.cards != shuffle(deck)
        hand_before_hit = len(hand2.cards)
        deck_before_hit = len(deck.cards)
        hit(hand2, 1)
        cards_app.session.commit()
        # do we still have 52 cards after hitting?
        assert len(set(deck.cards)) + len(set(hand2.cards)) == 52
        assert len(deck.cards) == deck_before_hit-1
        assert len(hand2.cards) == hand_before_hit+1

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
        deck = Hand()
        game.deck = deck
        game.deck.cards = piece_maker(suits, card_values, 1)
        game.deck.cards = shuffle(game.deck)
        player.hands.append(hand)
        player.cards.extend(cards)
        game.hands.append(hand)
        hand.cards.extend(cards)
        split(hand)
        hands = player.hands
        assert len(hands) == 2
        assert len(hands[0].cards) == 2 and len(hands[1].cards) == 2
        assert hands[0].cards[0].sequence == hands[1].cards[0].sequence

    def test_blackjack_player_wins(self):
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
        evaluate_hit(hand)
        cards_app.session.flush()
        # player wins with nautral evaluate_hit
        assert player.bank == bank_before_bet - 50
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
        evaluate_hit(hand)
        # player loses if he breaks
        assert player.bank == bank_after_bet
        # start of next loss, player stands on 15, dealer gets high hand
        hand.cards = [Card(sequence=10), Card(sequence=5)]
        bet(hand, 50)
        bank_after_bet = player.bank
        count_blackjack(hand)
        evaluate_hit(hand)
        assert player.bank == bank_after_bet
        # next loss condition, push

    def test_blackjack_payout(self):
        # game = Game('Blackjack')
        player.bank = 100
        game.deck = Hand()
        game.dealer = Player()
        game.dealer.hands.append(Hand())
        game.dealer.turns.append(Turn())
        game.hands.append(game.dealer.hands[0])
        player.hands.append(hand)
        game.hands.append(hand)
        game.deck.cards = piece_maker(suits, card_values, 1)
        game.players.append(player)
        cards_app.session.flush()
        # testing player AND dealer get blackjack
        hand.cards = [Card(sequence=1), Card(sequence=10)]
        game.dealer.hands[0].cards = [Card(sequence=1), Card(sequence=10)]
        bet(hand, 50)
        count_blackjack(hand)
        blackjack_dealer(game)
        blackjack_payout(game)
        assert player.bank == 100
        # Player gets 15 and dealer gets 15, dealer hits and breaks because deck is unshuffled and king on top
        hand.cards = [Card(sequence=10), Card(sequence=5)]
        game.dealer.hands[0].cards = [Card(sequence=10), Card(sequence=5)]
        bet(hand, 50)
        count_blackjack(hand)
        blackjack_dealer(game)
        blackjack_payout(game)
        assert player.bank == 150
        # player gets blackjack, dealer doesn't
        hand.bet = 0
        player.bank = 100
        hand.cards = [Card(sequence=10), Card(sequence=1)]
        game.dealer.hands[0].cards = [Card(sequence=10), Card(sequence=10)]
        bet(hand, 50)
        count_blackjack(hand)
        blackjack_dealer(game)
        blackjack_payout(game)
        assert player.bank == 175
        # player broke, loses bet
        hand.bet = 0
        player.bank = 100
        hand.cards = [Card(sequence=10), Card(sequence=10), Card(sequence=10)]
        game.dealer.hands[0].cards = [Card(sequence=10), Card(sequence=10)]
        bet(hand, 50)
        count_blackjack(hand)
        blackjack_dealer(game)
        blackjack_payout(game)
        assert player.bank == 50
