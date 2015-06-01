from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr


Base = declarative_base()

Game_Player = Table('game_player', Base.metadata,
                    Column('game_id', Integer, ForeignKey('game.id')),
                    Column('player_id', Integer, ForeignKey('player.id')), )


class Player(Base):
    __tablename__ = 'player'
    id = Column('id', Integer, primary_key=True)
    first_name = Column('first_name', String(100))
    last_name = Column('last_name', String(100))
    hands = relationship('Hand', backref='player')
    turns = relationship('Turn', backref='player')
    cards = relationship('Card', backref='player')
    bank = Column('bank', Integer, default=100)

    @hybrid_property
    def fullname(self):
        return self.first_name + " " + self.last_name


class Game(Base):
    __tablename__ = 'game'
    id = Column('id', Integer, primary_key=True)
    players = relationship('Player', secondary='game_player', backref='games')
    hands = relationship('Hand', backref='game')
    turns = relationship('Turn', backref='game')
    turn_number = Column(Integer)
    dealer_id = Column(Integer, ForeignKey('player.id'))
    dealer = relationship("Player", backref=backref("game", uselist=False))
    deck = relationship("Hand", uselist=False, backref="owner")
    type = Column('type', String(80))
    pot = Column('pot', Integer)
    is_over = Column('is_over', Boolean(create_constraint=False))
    dealer_turn = Column(Boolean(create_constraint=False))

    def __init__(self, type):
        self.type = type

    @hybrid_property
    def stats(self):
        """
        Do stuff and return a dictionary of all the players results
        i.e. {'player_name':player.fullname, 'bank':player.bank, etc.}
        for use in showing current game's stats since most of the info
        that will be displayed will be deleted at the end of the game
        """
        pass


class Hand(Base):
    __tablename__ = 'hand'
    id = Column('id', Integer, primary_key=True)
    game_id = Column('game_id', Integer, ForeignKey('game.id'))
    player_id = Column('player_id', Integer, ForeignKey('player.id'))
    cards = relationship('Card', backref='hand')
    bet = Column('bet', Integer, default=0)
    score = Column('score', Integer)


class Card(Base):
    __tablename__ = 'Card'
    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    value = Column(String(80))
    sequence = Column(Integer)
    category = Column(String(80))


class Turn(Base):
    __tablename__ = 'turn'
    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    is_turn = Column(Boolean(create_constraint=False))
    turn_number = Column(Integer)