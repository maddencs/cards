from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import settings


Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_tables(engine):
    """"""
    Base.metadata.create_all(engine)


Game_Player_Hand = Table('game_player_hand', Base.metadata,
                         Column('game_id', Integer, ForeignKey('game.id')),
                         Column('player_id', Integer, ForeignKey('player.id')),
                         Column('hand_id', Integer, ForeignKey('hand.id')))




class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String(80), unique=True)
    pw_hash = Column(String(80))
    bank = Column(Integer)
    hands = relationship('Hand', secondary='game_player_hand')
    games = relationship('Game', secondary='game_player_hand')



class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    type = Column(String(80))
    players = relationship("Player", secondary='game_player_hand', backref=backref('game', uselist=False))
    # OR players = dictionary
    hands = relationship("Hand", secondary='game_player_hand')
    deck = Column(Integer, ForeignKey('hand.id'))
    turn = Integer
    # OR turn = Column(Integer, ForeignKey('player.id'))

    def __init__(self, type):
        self.type = type


class Hand(Base):
    __tablename__ = 'hand'
    id = Column(Integer, primary_key=True)
    pieces = relationship('Piece', back_populates='hand')
    # game = relationship('game', ForeignKey('game'))
    bet = Column(Integer, default=0)
    score = Column(Integer, default=0)


class Piece(Base):
    __tablename__ = 'piece'
    id = Column(Integer, primary_key=True)
    category = Column(String(80))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    hand = relationship("Hand", back_populates="pieces")
    sequence = Column(Integer, default=1)
    value = Column(String(100))
    player_id = Column(Integer, ForeignKey('player.id'))
