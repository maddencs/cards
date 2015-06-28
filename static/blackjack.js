/**
 * Created by cory on 6/26/15.
 */

var Player = function (player) {
        this.id = player['id'];
        this.username = player['username'];
        this.email = player['email'];
        this.bank = player['bank'];
        this.hands = {};
        this.addHands = function () {
            var hands = {};
            var handKeys = Object.keys(player['hands']);
            for (var i = 0; i < handKeys.length; i++) {
                var hand = new Hand(player['hands'][handKeys[i]]);
                this.hands[handKeys[i]] = hand;
                hand.addCards()
            }
        };
    };

    var Game = function (data) {
        this.id = data['game']['id'];
        this.data = data;
        this.current_turn = data['game']['current_turn'];
        this.dealer = new Player(data['game']['dealer']);
        this.deck = new Hand(data['game']['deck']);
        this.pot = data['game']['pot'];
        this.time = data['game']['time'];
        this.active = data['game']['active'];
        this.over = data['game']['over'];
        this.timeDelta = data['game']['time_delta'];
        this.seats = {};
        this.getPlayer = function (id) {
            var seatKeys = Object.keys(this.seats);
            for (var s = 0; s < seatKeys.length; s++) {
                if (this.seats[seatKeys[s]].playerID == String(id)) {
                    return this.seats[seatKeys[s]]['player']
                } else {
                    if (s == (seatKeys.length)) {
                        return null;
                    }
                }
            }
        };
        this.compile = function () {
            var seats = {};
            var seatKeys = Object.keys(data['seats']);
            this.deck.addCards();
            for (var i = 0; i < seatKeys.length; i++) {
                var seat = data['seats'][seatKeys[i]];
                var seat = new Seat(seat);
                this.seats[seatKeys[i]] = seat;
                if (seat.player) {
                    seat.player.addHands();
                }
            }
        };
    };

    var Seat = function (seat) {
        this.id = seat['id'];
        this.gameID = seat['game_id'];
        this.expired = seat['expired'];
        this.player = seat['player'] ? new Player(seat['player']) : null;
        this.seatNumber = seat['seat_number'];
        this.time = seat['time'];
    };

    var Hand = function (hand) {
        this.id = hand['id'];
        this.gameID = hand['game_id'];
        this.expired = hand['expired'];
        this.cards = {};
        this.drawHand = function () {
            var handDiv = handBox(this);
            var cardsDiv = handDiv.querySelector("div.cards");
            cardsDiv.innerHTML = "";
            for (var i = 0; i < this.cards.length; i++) {
                var card = this.cards[i].drawCard;
                card.classList.add('card');
                cardsDiv.appendChild(card);
            }
            return handDiv;
        };
        this.addCards = function () {
            var cards = {};
            var cardKeys = Object.keys(hand['cards']);
            for (var i = 0; i < cardKeys.length; i++) {
                this.cards[cardKeys[i]] = new Card(hand['cards'][cardKeys[i]]);
            }
        };
    };


    var Card = function (card) {
        this.category = card['category'];
        this.sequence = card['sequence'];
        this.value = card['value'];
        this.drawCard = function () {
            var cardStr = this.category.toLowerCase() + this.sequence;
            var cardDiv = document.createElement('div');
            cardDiv.classList.add(cardStr);
            return cardDiv;
        };
    };

    var handBox = function (hand) {
        var handDiv = document.createElement('div');
        var cardDiv = document.createElement('div');
        var moveDiv = document.createElement('div');
        var hitSpan = document.createElement('span');
        var standSpan = document.createElement('span');
        var splitSpan = document.createElement('span');
        var betDiv = document.createElement('div');
        var betForm = document.createElement('form');
        var betLabel = document.createElement('label');
        var betInput = document.createElement('input');
        var betSubmit = document.createElement('input');
        betForm.addEventListener('submit', betListener);
        betForm.setAttribute('handID', hand['id']);
        cardDiv.classList.add('cards');
        betDiv.appendChild(betForm);
        betForm.appendChild(betLabel);
        betForm.appendChild(betInput);
        betForm.appendChild(betSubmit);
        betInput.setAttribute('name', 'betValue');
        betInput.setAttribute('type', 'number');
        betSubmit.setAttribute('type', 'submit');
        betSubmit.setAttribute('value', 'Bet');
        handDiv.appendChild(cardDiv);
        handDiv.appendChild(moveDiv);
        moveDiv.appendChild(hitSpan);
        moveDiv.appendChild(standSpan);
        moveDiv.appendChild(splitSpan);
        handDiv.setAttribute('handID', hand['id']);
        return handDiv;
    };

    var sitListener = function (e) {
        $(e.target).parent().attr("player", "{{ current_user.pid }}");
        var seat = $(e.target).attr('number');
        $.post('/game/{{ game.id }}/seat/' + seat);
    };

    var betListener = function (e) {
        var betValue = $('input:first').val();
        var handID = e.target.getAttribute('handID');
        $.get('/bet', {hand_id: handID, bet_value: betValue});
    };

    var readyListener = function (e) {
        var seat = $(e.target).parent().attr('seat');
        $.post('/seat/ready/' + seat);
    };