from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from models import *
from lib import piece_maker

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    p = Player()
    session.add(p)
    session.commit()
    p.name = 'Cory'
    print(p.name)
    g = Game('BlackJack')
    session.add(g)
    session.commit()
    g.players.append(p)
    h = Hand()
    session.add(h)
    session.commit()
    suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
    card_values = ['Ace', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King']
    pieces = piece_maker(h, suits, card_values, 1)
    h_pieces = session.query(Piece).filter(Piece.hand == h).all()
    player = session.query(Player).filter(Player.games.any(id=g.id)).all()
    print(player[0].name)
    app.run()
