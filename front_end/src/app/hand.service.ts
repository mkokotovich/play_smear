import { Cookie } from 'ng2-cookies/ng2-cookies';
import { Injectable } from '@angular/core';

import { Bid} from './model/bid';
import { BidInfo } from './model/bid-info';
import { Card } from './model/card';
import { CardPlayed } from './model/card-played';
import { GameAndHand } from './model/game-and-hand';
import { GameAndUser } from './model/game-and-user';
import { GameHandUser } from './model/game-hand-user';
import { GameId } from './model/game-id';
import { GameUserCard } from './model/game-user-card';
import { GetTrump } from './model/get-trump';
import { HandInfo } from './model/hand-info';
import { HandResults } from './model/hand-results';
import { Player } from './model/player';
import { PlayerInfo } from './model/player-info';
import { PlayingInfo } from './model/playing-info';
import { SmearApiService } from './smear-api.service';
import { TrickResults } from './model/trick-results';
import { Trump } from './model/trump';

@Injectable()
export class HandService {
    private currentlyBidding: boolean;
    public showBidInput: boolean;
    public showTrumpInput: boolean;
    public allowBid: boolean;
    public allowTrumpSelection: boolean;
    public playersTurn: boolean;
    private cards: Card[];
    private selectedCard: Card;
    public allowSelection: boolean;
    private gameStatusMessage: string;
    private gameAndHand: GameAndHand;
    public gameAndUser: GameAndUser;
    private handMessage: string;
    public highBid = new Bid("", "", 0);
    public allBids = new Array<Bid>();
    public currentHighBid = 0;
    private bidder: string;
    private dealer: string;
    private waitingFor: string;
    private bidMessage: string;
    public playingInfo = new PlayingInfo(new Array<CardPlayed>(), "", false, new Card("", ""), "");
    public handId: string;
    public cardsPlayed = new Array<CardPlayed>();
    public trump: string;
    public displayTrickConfirmationButton: boolean;
    public enableTrickConfirmationButton: boolean;
    public displayNextHandButton: boolean;
    public enableNextHandButton: boolean;
    public nextHandButtonText: string;
    public showHandResults: boolean;
    public handResults: HandResults;
    public pointsToPlayTo : number;
    public teamId : number;
    public teamsEnabled : boolean = false;
    public numTeams : number;
    public graphPrefix: string;
    private players: Array<Player>;
    public alerts: any = [];

    constructor(public smearApiService :SmearApiService) {
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.allowTrumpSelection = false;
        this.playersTurn = false;
        this.currentlyBidding = false;
        this.displayTrickConfirmationButton = false;
        this.enableTrickConfirmationButton = false;
        this.displayNextHandButton = false;
        this.enableNextHandButton = false;
        this.showHandResults = false;
        this.highBid = new Bid("", "", 0);
        this.handMessage = "Waiting for cards...";
        this.graphPrefix = "";
    }

    resetHand(): void {
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.allowTrumpSelection = false;
        this.playersTurn = false;
        this.currentlyBidding = false;
        this.displayTrickConfirmationButton = false;
        this.enableTrickConfirmationButton = false;
        this.displayNextHandButton = false;
        this.enableNextHandButton = false;
        this.showHandResults = false;
        this.highBid = new Bid("", "", 0);
        this.handMessage = "";
        this.graphPrefix = "";
        this.gameAndUser = new GameAndUser("", "");
        this.pointsToPlayTo = 0;
        this.teamId = null;
        this.teamsEnabled = false;
        this.numTeams = 0;
        this.currentlyBidding = true;
        this.handResults = null;
    }

    setGameInfo(game_id: string, username: string, teamId: number, numTeams: number, pointsToPlayTo: number, graphPrefix: string): void {
        this.gameAndUser = new GameAndUser(game_id, username);
        this.pointsToPlayTo = pointsToPlayTo;
        this.graphPrefix = graphPrefix;
        this.teamId = teamId;
        if (teamId != null && teamId != undefined) {
            this.teamsEnabled = true;
        }
        this.numTeams = numTeams;
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.allowTrumpSelection = false;
        this.currentlyBidding = true;
        this.setHandMessage("Waiting for cards...");
    }

    setPlayers(players: Array<Player>): void {
        this.players = players;
    }

    startNewHand(): void {
        this.setGameStatus("Waiting for cards to be dealt");
        this.showHandResults = false;
        this.trump = "";
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.currentHighBid = 0;
        this.allowTrumpSelection = false;
        this.currentlyBidding = true;
        this.displayTrickConfirmationButton = false;
        this.enableTrickConfirmationButton = false;
        this.displayNextHandButton = false;
        this.enableNextHandButton = false;
        this.highBid = new Bid("", "", 0);
        this.cardsPlayed = new Array<CardPlayed>();
        this.playingInfo = new PlayingInfo(new Array<CardPlayed>(), "", false, new Card("", ""), "");

        // If we rejoined a game after a hand had finished, just straight to the hand summary
        let hand_finished = Cookie.get("hand_finished");
        if (hand_finished == "true") {
            this.currentlyBidding = false;
            this.handId = Cookie.get("hand_id");
            return this.getHighBidAtEndOfGameAfterRejoin();
        }
        this.getNewHand();
    }

    getHighBidAtEndOfGameAfterRejoin(): void {
        this.showBidInput = false;
        Cookie.set("bid_submitted", "true", 1);
        let gameAndHand = new GameAndHand(this.gameAndUser.game_id, this.handId);
        this.smearApiService.handGetHighBid(gameAndHand)
                            .subscribe( highBidInfo => this.highBidReceivedAtEndOfGameAfterRejoin(highBidInfo),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    highBidReceivedAtEndOfGameAfterRejoin(highBidInfo: BidInfo): void {
        this.highBid.username = highBidInfo.bidder;
        this.highBid.bid = highBidInfo.current_bid;
        this.allBids = highBidInfo.all_bids;
        let saved_trump = Cookie.get("trump");
        this.trump = saved_trump;
        return this.getHandResults();
    }

    getNewHand(): void {
        this.setHandMessage("Waiting for cards...");
        this.smearApiService.handDeal(this.gameAndUser)
                            .subscribe( handInfo => this.receiveHand(handInfo),
                                        err => this.handleHandError(err, "Unable to retrieve cards"));
    }

    receiveHand(handInfo: HandInfo): void {
        this.cards = handInfo.cards;
        this.handId = handInfo.hand_id;
        this.setHandMessage("Your hand:");
        let bid_submitted = Cookie.get("bid_submitted");
        Cookie.set("hand_id", this.handId, 1);
        if (bid_submitted != "true") {
            this.setGameStatus("Waiting for your turn to bid");
            this.getBidInfo();
        } else {
            this.bidSubmitted();
        }
    }

    getBidInfo(): void {
        this.smearApiService.handGetBidInfo(this.gameAndUser)
                            .subscribe( bidInfo => this.receiveBidInfo(bidInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information about bidding"));
    }

    receiveBidInfo(bidInfo: BidInfo): void {
        if (bidInfo.all_bids != undefined) {
            this.allBids = bidInfo.all_bids;
        }
        if (bidInfo.dealer != undefined) {
            this.dealer = bidInfo.dealer;
        }
        if (bidInfo.waiting_for != undefined) {
            this.waitingFor = bidInfo.waiting_for;
        }
        if (bidInfo.ready == false) {
            // If we aren't ready, check again in two seconds
            setTimeout(this.getBidInfo.bind(this), 2000);
            return;
        }
        this.currentHighBid = bidInfo.current_bid;
        this.allowBid = true;
        this.playersTurn = true;
        this.showBidInput = true;
        this.setGameStatus("Enter your bid below");
        if (bidInfo.current_bid < 2) {
            if (bidInfo.force_two) {
                this.setBidMessage("No one has bid yet. Since you are the dealer, if you pass you will take an automatic two set.");
            } else {
                this.setBidMessage("No one has bid yet");
            }
        } else {
            this.setBidMessage(bidInfo.bidder + " has the highest bid of " + bidInfo.current_bid);
        }
    }

    declareBid(bidNum: number): void {
        let bid = new Bid(this.gameAndUser.game_id, this.gameAndUser.username, bidNum);
        this.playersTurn = false;
        this.setGameStatus("Submitting bid");
        this.setBidMessage("");
        this.smearApiService.handSubmitBid(bid)
                            .subscribe( res => this.bidSubmitted(),
                                        err => this.handleHandError(err, "Unable to submit bid"));
    }

    bidSubmitted(): void {
        this.showBidInput = false;
        Cookie.set("bid_submitted", "true", 1);
        this.setGameStatus("Bid submitted successfully. Waiting to discover the high bidder");
        let gameAndHand = new GameAndHand(this.gameAndUser.game_id, this.handId);
        this.smearApiService.handGetHighBid(gameAndHand)
                            .subscribe( highBidInfo => this.highBidReceived(highBidInfo),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    highBidReceived(highBidInfo: BidInfo): void {
        if (highBidInfo.all_bids != undefined) {
            this.allBids = highBidInfo.all_bids;
        }
        if (highBidInfo.waiting_for != undefined) {
            this.waitingFor = highBidInfo.waiting_for;
        }
        if (highBidInfo.ready == false) {
            // If we aren't ready, check again in two seconds
            setTimeout(this.bidSubmitted.bind(this), 2000);
            return;
        }
        // Reset the dealer so it only shows his/her bid at this point
        this.dealer = undefined;
        this.highBid.username = highBidInfo.bidder;
        this.highBid.bid = highBidInfo.current_bid;
        let saved_trump = Cookie.get("trump");
        if (saved_trump != "Spades" && saved_trump != "Clubs" && saved_trump != "Diamonds" && saved_trump != "Hearts") {
            this.setGameStatus("High bid received: " + this.highBid.username + " bid: " + this.highBid.bid);
            if (this.highBid.bid == 0) {
                this.setGameStatus("Dealer was forced to take a two set");
                // TODO: Handle the case where bid == 0 - a forced two set
                this.startNextHand();
            } else if (this.highBid.username == this.gameAndUser.username) {
                this.setGameStatus("You are the bidder, enter your choice for trump below");
                this.allowTrumpSelection = true;
                this.showTrumpInput = true;
                this.playersTurn = true;
            } else {
                this.setGameStatus(this.highBid.username + " bid: " + this.highBid.bid + ". Finding out what trump will be");
                this.getOrSubmitTrump("");
            }
        } else {
            this.trumpReceived(new Trump(saved_trump));
        }
    }

    submitTrump(trump: string): void {
        this.setGameStatus("Submitting trump to be " + trump);
        this.waitingFor = "";
        this.allowTrumpSelection = false;
        this.playersTurn = false;
        this.getOrSubmitTrump(trump);
    }

    getOrSubmitTrump(trump: string): void {
        let getTrump = new GetTrump(this.gameAndUser.game_id, this.gameAndUser.username, trump);
        this.smearApiService.handGetTrump(getTrump)
                            .subscribe( trump => this.trumpReceived(trump),
                                        err => this.handleHandError(err, "Unable to get or submit Trump"));
    }

    trumpReceived(trump: Trump): void {
        this.trump = trump.trump;
        Cookie.set("trump", this.trump, 1);
        this.setGameStatus("Trump is " + this.trump + ", waiting for your turn");
        this.showTrumpInput = false;
        this.currentlyBidding = false;
        this.getPlayingInfo();
    }

    getPlayingInfo(): void {
        this.setGameStatus("Trump is " + this.trump + ", waiting for your turn");
        this.smearApiService.handGetPlayingInfo(this.gameAndUser)
                            .subscribe( playingInfo => this.receivePlayingInfo(playingInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information needed for playing"));
    }

    receivePlayingInfo(playingInfo: PlayingInfo): void {
        if (playingInfo.cards_played != undefined) {
            this.cardsPlayed = playingInfo.cards_played;
        }
        if (playingInfo.waiting_for != undefined) {
            this.waitingFor = playingInfo.waiting_for;
        }
        if (playingInfo.ready_to_play == false) {
            // If we aren't ready, check again in two seconds
            setTimeout(this.getPlayingInfo.bind(this), 2000);
            return;
        }
        this.displayTrickConfirmationButton = false;
        this.allowSelections(true);
        this.playersTurn = true;
        this.playingInfo = playingInfo;
        if (playingInfo.lead_suit != "") {
            this.setGameStatus("Trump is " + this.trump + ", " + playingInfo.lead_suit + " was lead");
        } else {
            this.setGameStatus("Trump is " + this.trump + ", it is your lead");
        }
    }

    submitCardToPlay(cardToPlay: Card): void {
        this.setGameStatus("Submitting card");
        this.allowSelections(false);
        this.playersTurn = false;
        this.unSelectCard();
        this.deleteCard(cardToPlay);
        if (this.cards.length == 0) {
            this.setHandMessage("");
            Cookie.set("hand_finished", "true", 1);
        }
        let gameUserCard = new GameUserCard(this.gameAndUser.game_id, this.gameAndUser.username, cardToPlay);
        this.smearApiService.handSubmitCardToPlay(gameUserCard)
                            .subscribe( res => this.cardSubmitted(),
                                        err => this.handleSubmitCardError(err, cardToPlay));
    }

    handleSubmitCardError(err: any, card: Card): void {
        let message = <string>err;
        if (this.playingInfo.lead_suit != "") {
            message += ". Trump is " + this.trump + ", " + this.playingInfo.lead_suit + " was lead.";
        } else {
            message += ". Trump is " + this.trump + ", it is your lead.";
        }
        this.addCard(card);
        this.allowSelections(true);
        this.playersTurn = true;
        this.gameStatusMessage = message;
        console.log(err);
    }

    cardSubmitted(): void {
        this.setGameStatus("Card submitted successfully, waiting for results of trick");
        // Get trick results
        this.smearApiService.handGetTrickResults(this.gameAndUser)
                            .subscribe( trickResults => this.trickResultsReceived(trickResults),
                                        err => this.handleHandError(err, "Unable to get the results of the trick"));
    }

    trickResultsReceived(trickResults: TrickResults): void {
        if (trickResults.cards_played != undefined) {
            this.cardsPlayed = trickResults.cards_played;
        }
        if (trickResults.waiting_for != undefined) {
            this.waitingFor = trickResults.waiting_for;
        }
        if (trickResults.trick_finished == false) {
            setTimeout(this.cardSubmitted.bind(this), 2000);
            return;
        }
        this.waitingFor = "";
        this.setGameStatus("Trick is finished, " + trickResults.winner + " took the trick");
        this.displayTrickConfirmationButton = true;
        this.enableTrickConfirmationButton = true;
    }

    startNextTrick(): void {
        if (this.cards.length == 0) {
            return this.getHandResults();
        }
        this.playersTurn = false;
        this.enableTrickConfirmationButton = false;
        this.displayTrickConfirmationButton = false;
        this.cardsPlayed = new Array<CardPlayed>();
        this.getPlayingInfo();
    }

    getHandResults(): void {
        this.setGameStatus("Retrieving results of hand");
        this.waitingFor = "";
        this.setHandMessage("");
        let gameHandUser = new GameHandUser(this.gameAndUser.game_id, this.handId, this.gameAndUser.username);
        this.smearApiService.handGetResults(gameHandUser)
                            .subscribe( handResults => this.receiveHandResults(handResults),
                                        err => this.handleHandError(err, "Unable to retrieve results of hand"));
    }

    receiveHandResults(handResults: HandResults): void {
        this.handResults = handResults;
        this.trump = "";
        if (this.handResults.is_game_over) {
            this.setGameStatus("Game over.  " + this.handResults.overall_winner + " won!");
            this.displayNextHandButton = false;
            this.enableNextHandButton = false;
        } else {
            this.setGameStatus("");
            this.nextHandButtonText = "Start next hand";
            this.displayNextHandButton = true;
            this.enableNextHandButton = true;
        }
        this.showHandResults = true;
        this.displayTrickConfirmationButton = false;
        this.cardsPlayed = new Array<CardPlayed>();

        // Update scores and add game points
        for (let player of this.players) {
            player.points = new Array<string>();

            for (let playerInfo of this.handResults.player_infos) {
                if (player.name == playerInfo.username) {
                    player.score = playerInfo.score;
                    player.points.push("Game points: " + playerInfo.game_points);
                }
            }
        }

        // Update points won for UI
        for (let player of this.players) {
            if (this.handResults.high_winner == player.name) {
                player.points.push("Won High");
            }
            if (this.handResults.low_winner == player.name) {
                player.points.push("Won Low");
            }
            if (this.handResults.jack_winner == player.name) {
                player.points.push("Won Jack");
            }
            if (this.handResults.jick_winner == player.name) {
                player.points.push("Won Jick");
            }
            if (this.handResults.game_winner == player.name) {
                player.points.push("Won Game");
            }

            if (this.highBid.username == player.name && this.handResults.bidder_set) {
                player.points.push("Was set!");
            }

            if (this.highBid.username == player.name && !this.handResults.bidder_set) {
                player.points.push("Made bid!");
            }
        }

    }

    getPointsWon(player: string): Array<string> {
        for (let p of this.players) {
            if (p.name == player) {
                return p.points;
            }
        }
        return new Array<string>();
    }

    startNextHand(): void {
        this.enableNextHandButton = false;
        this.showHandResults = false;
        this.playersTurn = false;
        Cookie.set("bid_submitted", "false", 1);
        Cookie.set("trump", "", 1);
        Cookie.set("hand_finished", "false", 1);
        Cookie.set("hand_id", "", 1);
        this.allBids = new Array<Bid>();
        for (let player of this.players) {
            player.points = new Array<string>();
        }
        this.startNewHand();

    }

    handleHandError(err: any, message: string): void {
        this.gameStatusMessage = message + <string>err;
        console.log(err);
    }

    hasPlayerBid(player: string): boolean {
        for (let bid of this.allBids) {
            if (bid.username == player) {
                return true;
            }
        }
        // If a bid wasn't found
        return false;
    }

    getBidForPlayer(player: string): string {
        for (let bid of this.allBids) {
            if (bid.username == player) {
                if (bid.bid == 0) {
                    return "passed";
                } else {
                    return "bid " + bid.bid;
                }
            }
        }
        // If a bid wasn't found
        return "bid unknown";
    }

    isPlayerLead(player: string): boolean {
        for (let cp of this.cardsPlayed) {
            if (cp.username == player) {
                return true;
            } else {
                return false;
            }
        }
        // If a card wasn't found
        return false;
    }

    hasPlayerPlayedACard(player: string): boolean {
        for (let cp of this.cardsPlayed) {
            if (cp.username == player) {
                return true;
            }
        }
        // If a card wasn't found
        return false;
    }

    getCardPlayedForPlayer(player: string): Card {
        for (let cp of this.cardsPlayed) {
            if (cp.username == player) {
                return cp.card;
            }
        }
        // If a card wasn't found
        return new Card("", "");
    }

    getCards(): Card[] {
        return this.cards;
    }

    isCardSelected(): boolean {
        return this.selectedCard !== undefined;
    }

    getSelectedCard(): Card {
        return this.selectedCard;
    }

    selectCard(card: Card):void {
        if (this.allowSelection) {
            if (this.selectedCard == card) {
                // If the user clicks on a card that is already selected, play it
                this.submitCardToPlay(card);
            } else {
                this.selectedCard = card;
            }
        }
    }

    unSelectCard():void {
        this.selectedCard = undefined;
    }

    deleteCard(card:Card): void {
        this.cards.splice(this.cards.indexOf(card), 1);
    }

    addCard(card:Card): void {
        this.cards.push(card);
    }

    allowSelections(selections: boolean): void {
        this.allowSelection = selections;
    }

    setGameStatus(message: string):void {
        this.gameStatusMessage = message;
        //Clear array first
        //this.alerts.length = 0;
        //Add new alert
        //this.alerts.push({
            //type: 'info',
            //msg: `${message}`
        //});
    }

    getGameStatus(): string {
        return this.gameStatusMessage;
    }

    getHandMessage(): string {
        return this.handMessage;
    }

    setHandMessage(message:string): void {
        this.handMessage = message;
    }

    setBidMessage(message:string): void {
        this.bidMessage = message;
    }

    getBidMessage(): string {
        return this.bidMessage;
    }

    isBidding(): boolean {
        return this.currentlyBidding;
    }

    getTeamColorName(playerIndex: number): string {
        let color=""
        let teamId = playerIndex % this.numTeams;
        switch (teamId) {
            case 0:
                color="Blue";
                break;
            case 1:
                color="Orange";
                break;
            case 2:
                color="Plum";
                break;
            case 3:
                color="Sienna";
                break;
            //These shouldn't be used, but just in case someone puts one person per team
            case 4:
                color="Khaki";
                break;
            case 5:
                color="Linen";
                break;
            case 6:
                color="Cyan";
                break;
            case 7:
                color="Green";
                break;
            default:
                color=teamId.toString()
                break;
        }
        return color;
    }
}
