__author__ = 'cory'
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from wtforms import Form, StringField, PasswordField
from flask.ext.login import UserMixin

Base = declarative_base()

Game_Player = Table('game_player', Base.metadata,
                    Column('game_id', Integer, ForeignKey('game.id')),
                    Column('player_id', Integer, ForeignKey('player.pid')), )


class GameRoom(Base):
    __tablename__ = 'gameroom'
    id = Column(Integer, primary_key=True)
    current_game_id = Column(Integer, ForeignKey('game.id'))
    current_game = relationship('Game', backref=backref('room'), uselist=False)


class Seat(Base):
    __tablename__ = 'seating'
    id = Column(Integer, primary_key=True)
    seat_number = Column(Integer)
    player_id = Column(Integer, ForeignKey('player.pid'))
    player = relationship('Player', backref=backref('seats'), uselist=False)
    game_id = Column(Integer, ForeignKey('game.id'))
    ready = Column(Boolean(create_constraint=True))
    time = Column(DateTime(timezone=False))
    expired = Column(Boolean(create_constraint=False))

    def __init__(self, seat):
        self.seat_number = seat

    @hybrid_property
    def details(self):
        details = {'id': self.id,
                   'time': self.time,
                   'expired': self.expired,
                   'ready': self.ready,
                   'seat_number': self.seat_number,
                   'game_id': self.game_id}
        if self.player:
            details['player'] = self.player.details
            for hand in self.player.hands:
                if hand.game_id == self.game_id:
                    details['player']['hands'][hand.id] = hand.details
        return details


class Player(UserMixin, Base):
    __tablename__ = 'player'
    email = Column('email', String(80), unique=True)
    username = Column('username', String(20), unique=True)
    pid = Column(Integer, primary_key=True)
    # hands = relationship('Hand', backref='player')
    cards = relationship('Card', backref='player')
    bank = Column('bank', Integer, default=100)
    password = Column('password', String(255))
    authenticated = Column(Boolean(create_constraint=False))

    @hybrid_property
    def details(self):
        return {'email': self.email,
                'username': self.username,
                'pid': self.pid,
                'bank': self.bank,
                'hands': {}}

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Game(Base):
    __tablename__ = 'game'
    id = Column('id', Integer, primary_key=True)
    players = relationship('Player', secondary='game_player', backref='games')
    hands = relationship('Hand', backref='game')
    dealer_id = Column(Integer, ForeignKey('player.pid'))
    dealer = relationship("Player", backref=backref("game", uselist=False))
    deck = relationship("Hand", uselist=False, backref="owner")
    type = Column('type', String(80))
    pot = Column('pot', Integer)
    is_over = Column('is_over', Boolean(create_constraint=False))
    dealer_turn = Column(Boolean(create_constraint=False))
    active = Column(Boolean(create_constraint=False))
    seats = relationship('Seat', backref='game')
    current_turn = Column(Integer)
    time = Column(DateTime(timezone=False))

    def __init__(self, game_type):
        self.type = game_type
        self.pot = 0

    @hybrid_property
    def stats(self):
        result = {'game': {'id': self.id,
                           'time': self.time,
                           'over': self.is_over,
                           'active': self.active,
                           'current_turn': self.current_turn,
                           'deck': {'cards': []},
                           'dealer': {'hand': {
                               'cards': [],
                               'score': self.dealer.hands[0].score,
                               'is_turn': self.dealer.hands[0].is_turn,
                               'expired': self.dealer.hands[0].is_expired,
                           }},
                           'pot': self.pot},
                  'seats': {},
                  'players': {}}
        if self.deck:
            for card in self.deck.cards:
                card_dict = {'seq': card.sequence,
                             'value': card.value,
                             'category': card.category}
                result['game']['deck']['cards'].append(card_dict)
        if self.seats:
            for seat in self.seats:
                result['seats'][str(seat.seat_number)] = seat.details
        if self.dealer.hands[0].cards:
            for card in self.dealer.hands[0].cards:
                card_dict = {'seq': card.sequence,
                             'value': card.value,
                             'category': card.category}
                result['game']['dealer']['hand']['cards'].append(card_dict)
        # for player in self.players:
        #     result['players'][str(player.pid)] = player.details
        #     result['players'][str(player.pid)]['hands'] = {}
        #     for hand in player.hands:
        #         if hand.game_id == self.id:
        #             result['players'][str(player.pid)]['hands'][str(hand.id)] = hand.details
        return result


class Hand(Base):
    __tablename__ = 'hand'
    id = Column('id', Integer, primary_key=True)
    game_id = Column('game_id', Integer, ForeignKey('game.id'))
    player_id = Column('player_id', Integer, ForeignKey('player.pid'))
    player = relationship('Player', backref=backref('hands'), uselist=False)
    cards = relationship('Card', backref='hand')
    bet = Column('bet', Integer)
    score = Column('score', Integer)
    is_turn = Column(Boolean(create_constraint=False))
    is_expired = Column(Boolean(create_constraint=False))

    @hybrid_property
    def details(self):
        result = {'game_id': self.game_id,
                  'id': self.id,
                  'cards': [],
                  'bet': self.bet,
                  'score': self.score,
                  'is_turn': self.is_turn,
                  'is_expired': self.is_expired}
        for card in self.cards:
            result['cards'].append(card.details)
        return result

    def __init__(self):
        self.bet = 0
        self.score = 0


class Card(Base):
    __tablename__ = 'card'
    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.pid'))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    value = Column(String(80))
    sequence = Column(Integer)
    category = Column(String(80))
    temp_value = Column(Integer)

    @hybrid_property
    def details(self):
        return {'id': self.id,
                'player_id': self.player_id,
                'hand_id': self.hand_id,
                'value': self.value,
                'sequence': self.sequence,
                'category': self.category,
                'temp_value': self.temp_value}


"""
                Login Form section
"""


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
