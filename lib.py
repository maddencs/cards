from models import *

def piece_maker(hand, category, values, decks):
    i = 0
    while i < decks:
        for c in category:
            for v in values:
                p = Piece(category=c, sequence=(values.index(v)+1), value=v)
                hand.pieces.append(p)
        i += 1
    return hand.pieces