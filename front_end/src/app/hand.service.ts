import { Injectable } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

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
import { HandStatusModalComponent } from './hand-status-modal/hand-status-modal.component';
import { Player } from './model/player';
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
    private cards: Card[];
    private selectedCard: Card;
    private allowSelection: boolean;
    private gameStatusMessage: string;
    private gameAndHand: GameAndHand;
    private gameAndUser: GameAndUser;
    private handMessage: string;
    public highBid = new Bid("", "", 0);
    public allBids = new Array<Bid>();
    private bidder: string;
    private bidMessage: string;
    public playingInfo = new PlayingInfo(new Array<CardPlayed>(), new Card("", ""), "");
    private handId: string;
    public cardsPlayed = new Array<CardPlayed>();
    private trump: string;
    public displayTrickConfirmationButton: boolean;
    public enableTrickConfirmationButton: boolean;
    public displayNextHandButton: boolean;
    public enableNextHandButton: boolean;
    public nextHandButtonText: string;
    public showHandResults: boolean;
    private handResults: HandResults;
    private players: Array<Player>;
    public alerts: any = [];

    constructor(private smearApiService :SmearApiService,
                private modalService: NgbModal) {
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.allowTrumpSelection = false;
        this.currentlyBidding = false;
        this.displayTrickConfirmationButton = false;
        this.enableTrickConfirmationButton = false;
        this.displayNextHandButton = false;
        this.enableNextHandButton = false;
        this.showHandResults = false;
        this.highBid = new Bid("", "", 0);
        this.handMessage = "Waiting for cards...";
    }

    setGameInfo(gameAndUser: GameAndUser): void {
        this.gameAndUser = gameAndUser;
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

    displayHandStatusModal(message: string) {
        const modalRef = this.modalService.open(HandStatusModalComponent);
        modalRef.componentInstance.handStatus = message;
    }

    startNewHand(): void {
        this.setGameStatus("Waiting for cards to be dealt");
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.allowTrumpSelection = false;
        this.currentlyBidding = true;
        this.displayTrickConfirmationButton = false;
        this.enableTrickConfirmationButton = false;
        this.displayNextHandButton = false;
        this.enableNextHandButton = false;
        this.highBid = new Bid("", "", 0);
        this.cardsPlayed = new Array<CardPlayed>();
        this.playingInfo = new PlayingInfo(new Array<CardPlayed>(), new Card("", ""), "");

        this.getNewHand();
    }

    getNewHand(): void {
        this.setHandMessage("Waiting for cards...");
        this.smearApiService.handDeal(this.gameAndUser)
                            .subscribe( handInfo => this.receiveHand(handInfo),
                                        err => this.handleHandError(err, "Unable to retrieve cards"));
    }

    receiveHand(handInfo: HandInfo) {
        this.cards = handInfo.cards;
        this.handId = handInfo.hand_id;
        this.showBidInput = true;
        this.setHandMessage("Your hand:");
        this.setGameStatus("Waiting for your turn to bid");
        this.getBidInfo();
    }

    getBidInfo(): void {
        this.smearApiService.handGetBidInfo(this.gameAndUser)
                            .subscribe( bidInfo => this.receiveBidInfo(bidInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information about bidding"));
    }

    receiveBidInfo(bidInfo: BidInfo) {
        this.allBids = bidInfo.all_bids;
        this.allowBid = true;
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
        this.setGameStatus("Submitting bid");
        this.setBidMessage("");
        this.smearApiService.handSubmitBid(bid)
                            .subscribe( res => this.bidSubmitted(),
                                        err => this.handleHandError(err, "Unable to submit bid"));
    }

    bidSubmitted(): void {
        this.showBidInput = false;
        this.setGameStatus("Bid submitted successfully. Waiting to discover the high bidder");
        let gameAndHand = new GameAndHand(this.gameAndUser.game_id, this.handId);
        this.smearApiService.handGetHighBid(gameAndHand)
                            .subscribe( highBidInfo => this.highBidReceived(highBidInfo),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    highBidReceived(highBidInfo: BidInfo): void {
        this.highBid.username = highBidInfo.bidder;
        this.highBid.bid = highBidInfo.current_bid;
        this.allBids = highBidInfo.all_bids;
        this.setGameStatus("High bid received: " + this.highBid.username + " bid: " + this.highBid.bid);
        if (this.highBid.bid == 0) {
            // Handle the case where bid == 0 - a forced two set
            this.setGameStatus("Dealer was forced to take a two set");
        } else if (this.highBid.username == this.gameAndUser.username) {
            this.setGameStatus("You are the bidder, enter your choice for trump below");
            this.allowTrumpSelection = true;
            this.showTrumpInput = true;
        } else {
            this.setGameStatus("Finding out what trump will be");
            this.getOrSubmitTrump("");
        }
    }

    submitTrump(trump: string): void {
        this.setGameStatus("Submitting trump to be " + trump);
        this.allowTrumpSelection = false;
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

    receivePlayingInfo(playingInfo: PlayingInfo) {
        this.displayTrickConfirmationButton = false;
        this.allowSelections(true);
        this.cardsPlayed = playingInfo.cards_played;
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
        this.unSelectCard();
        this.deleteCard(cardToPlay);
        if (this.cards.length == 0) {
            this.setHandMessage("");
        }
        let gameUserCard = new GameUserCard(this.gameAndUser.game_id, this.gameAndUser.username, cardToPlay);
        this.smearApiService.handSubmitCardToPlay(gameUserCard)
                            .subscribe( res => this.cardSubmitted(),
                                        err => this.handleHandError(err, "Unable to submit card to play"));
    }

    cardSubmitted(): void {
        this.setGameStatus("Card submitted successfully, waiting for results of trick");
        // Get trick results
        this.smearApiService.handGetTrickResults(this.gameAndUser)
                            .subscribe( trickResults => this.trickResultsReceived(trickResults),
                                        err => this.handleHandError(err, "Unable to get the results of the trick"));
    }

    trickResultsReceived(trickResults: TrickResults) {
        this.setGameStatus("Trick is finished, " + trickResults.winner + " took the trick");
        // This wasn't working very well.
        //this.displayHandStatusModal("Trick is finished, " + trickResults.winner + " took the trick");
        this.cardsPlayed = trickResults.cards_played;
        this.displayTrickConfirmationButton = true;
        this.enableTrickConfirmationButton = true;
    }

    startNextTrick() {
        if (this.cards.length == 0) {
            return this.getHandResults();
        }
        this.enableTrickConfirmationButton = false;
        this.cardsPlayed = new Array<CardPlayed>();
        this.getPlayingInfo();
    }

    getHandResults(): void {
        this.setGameStatus("Retrieving results of hand");
        this.setHandMessage("");
        let gameHandUser = new GameHandUser(this.gameAndUser.game_id, this.handId, this.gameAndUser.username);
        this.smearApiService.handGetResults(gameHandUser)
                            .subscribe( handResults => this.receiveHandResults(handResults),
                                        err => this.handleHandError(err, "Unable to retrieve results of hand"));
    }

    receiveHandResults(handResults: HandResults) {
        this.setGameStatus("Results of previous hand");
        this.handResults = handResults;
        if (this.handResults.is_game_over) {
            this.setGameStatus("Results of previous hand. Game is now over.");
            this.displayNextHandButton = false;
            this.enableNextHandButton = false;
        } else {
            this.setGameStatus("Results of previous hand");
            this.nextHandButtonText = "Start next hand";
            this.displayNextHandButton = true;
            this.enableNextHandButton = true;
        }
        this.showHandResults = true;
        this.displayTrickConfirmationButton = false;
        this.cardsPlayed = new Array<CardPlayed>();

        // Update scores
        for (let player of this.players) {
            let pointsWon = 0

            player.points = new Array<string>();

            if (this.handResults.high_winner == player.name) {
                pointsWon += 1;
                player.points.push("Won High");
            }
            if (this.handResults.low_winner == player.name) {
                pointsWon += 1;
                player.points.push("Won Low");
            }
            if (this.handResults.jack_winner == player.name) {
                pointsWon += 1;
                player.points.push("Won Jack");
            }
            if (this.handResults.jick_winner == player.name) {
                pointsWon += 1;
                player.points.push("Won Jick");
            }
            if (this.handResults.game_winner == player.name) {
                pointsWon += 1;
                player.points.push("Won Game");
            }

            if (this.highBid.username == player.name && pointsWon < this.highBid.bid ) {
                player.addToScore(-this.highBid.bid);
                player.points.push("Was set!");
            } else {
                player.addToScore(pointsWon);
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

    startNextHand() {
        this.enableNextHandButton = false;
        this.startNewHand();
        for (let player of this.players) {
            player.points = new Array<string>();
        }

    }

    handleHandError(err: any, message: string) {
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

    hasPlayerPlayedACard(player: string): boolean {
        for (let cp of this.cardsPlayed) {
            if (cp.username == player) {
                return true;
            }
        }
        // If a card wasn't found
        return false;
    }

    getCardPlayedForPlayer(player: string): string {
        for (let cp of this.cardsPlayed) {
            if (cp.username == player) {
                return cp.card.value + " of " + cp.card.suit;
            }
        }
        // If a card wasn't found
        return "card not played";
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

    deleteCard(card:Card) {
        this.cards.splice(this.cards.indexOf(card), 1);
    }

    allowSelections(selections: boolean) {
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
}
