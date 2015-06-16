__author__ = 'cory'
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from wtforms import Form, StringField, HiddenField, PasswordField
from flask import request, url_for, redirect
from flask.ext.login import UserMixin
from urllib.parse import urlparse, urljoin
Base = declarative_base()

Game_Player = Table('game_player', Base.metadata,
                    Column('game_id', Integer, ForeignKey('game.id')),
                    Column('player_id', Integer, ForeignKey('player.pid')), )


class GameRoom(Base):
    __tablename__ = 'gameroom'
    id = Column('id', Integer, primary_key=True)
    game = relationship('Game', uselist=False, backref='room')
    game_id = Column(Integer, ForeignKey('game.id'))


class Player(UserMixin, Base):
    __tablename__ = 'player'
    email = Column('username', String(80))
    pid = Column(Integer, primary_key=True)
    hands = relationship('Hand', backref='player')
    cards = relationship('Card', backref='player')
    bank = Column('bank', Integer, default=100)
    password = Column('password', String(255))
    authenticated = Column(Boolean(create_constraint=False))

    def __init__(self, email, password):
        self.email = email
        self.password = password

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
    is_active = Column(Boolean(create_constraint=False))

    def __init__(self, type):
        self.type = type
        self.pot = 0

    @hybrid_property
    def stats(self):
        result = []
        for player in self.players:
            # hands = session.query(Hand).filter(Hand.game_id == self.id)\
            #     .filter(Hand.player_id == player.id)
            dict = {'player_name': player.username, 'bank': player.bank}
            result.append(dict)
        return result

class Hand(Base):
    __tablename__ = 'hand'
    id = Column('id', Integer, primary_key=True)
    game_id = Column('game_id', Integer, ForeignKey('game.id'))
    player_id = Column('player_id', Integer, ForeignKey('player.pid'))
    cards = relationship('Card', backref='hand')
    bet = Column('bet', Integer)
    score = Column('score', Integer)
    is_turn = Column(Boolean(create_constraint=False))
    is_expired = Column(Boolean(create_constraint=False))

    def __init__(self):
        self.bet = 0
        self.score = 0

class Card(Base):
    __tablename__ = 'Card'
    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.pid'))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    value = Column(String(80))
    sequence = Column(Integer)
    category = Column(String(80))
    temp_value = Column(Integer)

"""
                Login Form section
"""

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


# class RedirectForm(Form):
#     next = HiddenField()
#
#     def __init__(self, *args, **kwargs):
#         Form.__init__(self, *args, **kwargs)
#         if not self.next.data:
#             self.next.data = get_redirect_target() or ''
#
#     def redirect(self, endpoint='index', **values):
#         if is_safe_url(self.next.data):
#             return redirect(self.next.data)
#         target = get_redirect_target()
#         return redirect(target or url_for(endpoint, **values))


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
