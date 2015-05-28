import os
import cards_app
import unittest
import tempfile

class CardsTestCase(unittest.TestCase):

    def setUp(self):
        cards_app.app.self_fd, cards_app.app.config['DATABASE'] = tempfile.mkstemp()
        cards_app.app.config['TESTING'] = True
        self.app = cards_app.app.test_client()

    def tearDown(self):
        os.close(cards_app.app.self_fd)
        os.unlink(cards_app.app.config['DATABASE'])

    def test_shuffle(self):
        p = cards_app.Player()
        cards_app.session.add(p)
        cards_app.session.commit()
        p.name = 'Cory'
        g = cards_app.Game('BlackJack')
        cards_app.session.add(g)
        cards_app.session.commit()
        g.players.append(p)
        h = cards_app.Hand()
        cards_app.session.add(h)
        cards_app.session.commit()
        suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
        card_values = ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']
        pieces = cards_app.piece_maker(h, suits, card_values, 1)
        h_pieces = cards_app.session.query(cards_app.Piece).filter(cards_app.Piece.hand == h).all()
        player = cards_app.session.query(cards_app.Player).filter(cards_app.Player.games.any(id=g.id)).all()

if __name__ == '__main__':
    unittest.main()