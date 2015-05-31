from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()



Game_Player = Table('game_player', Base.metadata,
                         Column('game_id', Integer, ForeignKey('game.id')),
                         Column('player_id', Integer, ForeignKey('player.id')),)


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    hands = relationship('Hand', backref='player')
    turns = relationship('Turn', backref='player')
    cards = relationship('Card', uselist=False, backref='player')
    bank = Column(Integer, default=100)


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship('Player', secondary='game_player', backref='games')
    hands = relationship('Hand', backref='game')
    turns = relationship('Turn', backref='game')
    turn_number = Column(Integer)
    type = Column(String(80))
    pot = Column(Integer)
    is_over = Column(Boolean(create_constraint=False))

    def __init__(self, type):
        self.type = type


class Hand(Base):
    __tablename__ = 'hand'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    cards = relationship('Card', backref='hand')
    bet = Column(Integer)
    score = Column(Integer)


class Card(Base):
    __tablename__ = 'Card'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    value = Column(String(80))
    sequence = Column(Integer)
    category = Column(String(80))


class Turn(Base):
    __tablename__ = 'turn'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    is_turn = Column(Boolean(create_constraint=False))
    turn_number = Column(Integer)


# class GameRelations(Base):
#     id = Column(Integer, primary_key=True)
#     __tablename__ = 'game_relations'
#     game_id = Column(Integer, ForeignKey('game.id'), primary_key=True)
#     player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
#     hand_id = Column(Integer, ForeignKey('hand.id'), primary_key=True)
#     Card_id = Column(Integer, ForeignKey('Card.id'), primary_key=True)
#     player = relationship('Player', backref='game_relations')
#     hand = relationship('Hand', backref='game_relations')
#     Card = relationship('Card', backref='game_relations')


