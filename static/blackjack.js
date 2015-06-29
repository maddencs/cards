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
            hand.addCards();
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
            var seatData = data['seats'][seatKeys[i]];
            var seat = new Seat(seatData);
            this.seats[seatKeys[i]] = seat;
            if (seat.player) {
                if (seatData['player']['hands']) {
                    var handKeys = Object.keys(seatData['player']['hands']);
                    for (var k = 0; k < handKeys.length; k++) {
                        var hand = seatData['player']['hands'][handKeys[k]];
                        seat.player.hands[hand['id']] = new Hand(hand);
                        if (hand['cards']) {
                            var cardKeys = Object.keys(hand['cards']);
                            for (var c = 0; c < cardKeys.length; c++) {
                                var card = hand['cards'][cardKeys[c]];
                                seat.player.hands[hand['id']].cards[cardKeys[c]] = new Card(card);
                            }
                        }
                    }
                }
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
    this.sit = function () {
        var postURL = '/seat/' + seat.id;
        console.log(postURL);
        $.post(postURL);
    };
};

var Hand = function (hand) {
    this.id = hand['id'];
    this.gameID = hand['game_id'];
    this.expired = hand['expired'];
    this.cards = {};
    this.score = hand['score'];
    this.drawHand = function () {
        var handDiv = handBox(this);
        var cardsDiv = handDiv.querySelector("div.cards");
        var cardKeys = Object.keys(this.cards);
        for (var i = 0; i < cardKeys.length; i++) {
            var card = this.cards[cardKeys[i]].drawCard();
            console.log(card);
            cardsDiv.appendChild(card);
        }
        return handDiv;
    };
    this.addCards = function () {
        var cards = {};
        var cardKeys = Object.keys(hand['cards']);
        for (var i = 0; i < cardKeys.length; i++) {
            var card = new Card(hand['cards'][cardKeys[i]]);
            this.cards[cardKeys[i]] = card;
        }
    };
    this.bet = function (bet) {
        $.get('/bet', {hand_id: this.id, bet_value: bet})
            .done(function (data) {
                if (data['status'] == 'failed') {
                    // do whatever needs to be done if the bet fails
                } else if (data['status'] == 'success') {
                    // perform successful bet actions heref
                }
            })
    }
};

var Card = function (card) {
    this.category = card['category'];
    this.sequence = card['sequence'];
    this.value = card['value'];
    this.drawCard = function () {
        var cardStr = this.category.toLowerCase() + this.sequence;
        var cardDiv = document.createElement('div');
        cardDiv.classList.add('sprite');
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
    betForm = document.createElement('form');
    var betLabel = document.createElement('label');
    var betInput = document.createElement('input');
    var betSubmit = document.createElement('input');
    var scoreSpan = document.createElement('span');
    scoreSpan.innerHTML = 'Current hand score: ' + hand.score;
    handDiv.appendChild(scoreSpan);
    betForm.addEventListener('submit', hand.bet);
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