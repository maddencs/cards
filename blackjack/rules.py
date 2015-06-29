__author__ = 'cory'
from lib_dir.card_actions import hit

"""

                        Blackjack functions

"""

def count_blackjack(hand):
    hand.score = 0
    aces = []
    for card in hand.cards:
        if 2 <= card.sequence <= 10:
            hand.score += card.sequence
        elif card.sequence > 10:
            hand.score += 10
        else:
            aces.append(card)
    for ace in aces:
        if hand.score > 11:
            hand.score += 1
        else:
            ace.temp_value = 11
            hand.score += 11


# Evaluate blackjack hand for breaks
# not included in hit() for reuse of hit
def evaluate_hit(hand):
    game = hand.game
    player = hand.player
    if hand.score > 21:
        # break, lose bet
        pass
    elif hand.score == 21:
        pass
    elif len(hand.cards) == 5:
        # maybe let player win if they have five cards
        pass


def blackjack_dealer(game):
    dealer_hand = game.dealer.hands[0]
    count_blackjack(dealer_hand)
    # evaluating dealer's move
    if dealer_hand.score > 17:
        dealer_hand.is_turn = False
        blackjack_payout(game)
    # evaluate if dealer has any aces in his 17 making a soft 17 at which point he should hit
    elif dealer_hand.score == 17:
        for card in dealer_hand.cards:
            if card.temp_value == 11:
                hit(dealer_hand, 1)
                blackjack_dealer(game)
            else:
                blackjack_payout(game)
    elif dealer_hand.score < 17:
        hit(dealer_hand, 1)
        blackjack_dealer(game)
    if not dealer_hand.is_turn:
        blackjack_payout(game)


def blackjack_payout(game):
    """
    The game is over once this function completes
    need to figure out how I want to handle
    setting up the next game after payout
    """
    for player in game.players:
        # hands = session.query(Hand).filter(Hand.game == game).filter(Hand.player == player).all()
        for hand in game.hands:
            if not hand.is_expired:
                if hand.score < 21:
                    if game.dealer.hands[0].score < hand.score:
                        # Player wins, has high hand
                        player.bank += hand.bet * 2
                    elif game.dealer.hands[0].score == hand.score:
                        # Player pushes, has equal score to dealer
                        player.bank += hand.bet
                        hand.bet = 0
                    elif game.dealer.hands[0].score > 21:
                        player.bank += hand.bet
                    elif 21 > game.dealer.hands[0].score > hand.score:
                        # dealer wins, high hand
                        hand.bet = 0
                elif hand.score == 21:
                    if game.dealer.hands[0].score == 21:
                        if len(game.dealer.hands[0].cards) == 2 and len(hand.cards) == 2:
                            # Dealer and player get blackjack, push
                            player.bank += hand.bet
                        elif len(game.dealer.hands[0].cards) == 2 and len(hand.cards) > 2:
                            # player gets 21, but dealer gets blackjack, player loses
                            hand.bet = 0
                    elif len(hand.cards) > 2:
                        # player has 21, but not blackjack
                        player.score += hand.bet * 2
                    elif len(hand.cards) == 2:
                        # player has blackjack
                        player.bank += hand.bet * 2.5
                hand.is_expired = True

