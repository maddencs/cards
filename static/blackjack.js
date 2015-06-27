/**
 * Created by cory on 6/26/15.
 */
var Game = function (data) {
    this.id = data['game']['id'];
    this.data = data;
    this.current_turn = data['game']['current_turn'];
    this.dealer = new Player(data['game']['dealer']);
    this.deck = data['game']['deck'];
    this.pot = data['game']['pot'];
    this.time = data['game']['time'];
    this.active = data['game']['active'];
    this.over = data['game']['over'];
    this.players = [];
    this.seats = [];
    this.timeDelta = data['game']['time_delta'];
};

var Player = function (player) {
    this.id = player['id'];
    this.username = player['username'];
    this.email = player['email'];
    this.bank = player['bank'];
    this.hands = [];
};

Player.prototype = new Game;

var Hand = function (hand) {
    this.id = hand['id'];
    this.cards = [];
    this.gameID = hand['game_id'];
    this.expired = hand['expired'];
};

Hand.prototype = new Player;

var Card = function (card) {
    this.category = card['category'];
    this.sequence = card['seq'];
    this.value = card['value']
};

var Seat = function (seat) {
    this.id = seat['id'];
    this.gameID = seat['game_id'];
    this.expired = seat['expired'];
    this.playerID = seat['player_id'];
    this.seatNumber = seat['seat_number'];
    this.time = seat['time'];
};

Game.prototype.addPlayers = function () {
    var player_keys = Object.keys(this.data['playes']);
    for (var i = 0; i < player_keys.length; i++) {
        var index = player_keys[i];
        this.players.append(new Player(this.data['players']['index']));
    }
};

Player.prototype.addHands = function () {
    var player = this.data['players'][this.id];
    var hand_keys = Object.keys(player['hands']);
    for (var i = 0; i < hand_keys.length; i++) {
        if (!(hand_keys[i] in this.hands)) {
            this.hands.append(new Hand(player[hand_keys[i]]))
        }
    }
};

Game.prototype.addSeats = function () {
    this.seat_keys = Object.keys(this.seats);
    for (var i = 0; i < this.seat_keys.length; i++) {
        if (!(this.seat_keys[i] in this.seats)) {
            this.seats.append(new Seat(this.seats[i]));
        }
    }
};

Hand.prototype.addCards = function () {
    var cards = this.data['hands'][this.id]['cards'];
    var card_keys = Object.keys(cards);
    for (var i = 0; i < card_keys.length; i++) {
        if (!(card_keys[i] in this.cards)) {
            this.cards.append(cards[i]);
        }
    }
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
    var sitSpans = document.querySelectorAll("span[id='sitSpan']");
    $(sitSpans).remove();
    var parentDiv = $(e.target).parent();
    var readyButton = document.createElement('button');
    var seat = $(e.target).attr('number');
    readyButton.addEventListener('click', readyListener);
    readyButton.innerHTML = 'Ready';
    readyButton.setAttribute('seat', $(e.target).parent().attr('seat'));
    parentDiv.append(readyButton);
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

Card.prototype.drawCard = function () {
    var cardStr = this.category.toLowerCase() + this.sequence;
    var cardDiv = document.createElement('div');
    cardDiv.classList.add(cardStr);
    return cardDiv;
};

Hand.prototype.drawHand = function () {
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

//var updateData = function(dataURL, frequency) {
//    var request = new XMLHttpRequest();
//    var onRequestChange = function () {
//            if ((request.readyState == 4) && (request.status == 200)) {
//                var data = JSON.parse(request.responseText);
//                var a = JSON.stringify(data);
//                var b = JSON.stringify(window.currentData);
//                $('#start').html = 'Game started ' + data['time_delta'] + ' ago';
//                if (a != b) {
//                    window.currentData = data;
//                    window.callback(data);
//                } else {
//                    console.log(a == b);
//                }
//            }
//        };
//
//    var getData = function () {
//        request.onreadystatechange = onRequestChange;
//        request.open('GET', dataURL, true);
//        request.send();
//    };
//
//    var dataTimer = setInterval(function () {
//        getData();
//    }, frequency);
//
//    dataTimer();
//};

Game.prototype.getPlayer = function(id){
    for(var i=0; i < this.players.length; i++){
        if(this.players[i].id == id){
            return this.players[i];
        } else {
            if(i==(this.players.length-1)){
                return null;
            }
        }
    }
};