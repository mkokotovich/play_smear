import { Injectable } from '@angular/core';

import { Bid} from './model/bid';
import { BidInfo } from './model/bid-info';
import { Card } from './model/card';
import { GameAndHand } from './model/game-and-hand';
import { GameAndUser } from './model/game-and-user';
import { GameId } from './model/game-id';
import { GetTrump } from './model/get-trump';
import { HandInfo } from './model/hand-info';
import { PlayingInfo } from './model/playing-info';
import { SmearApiService } from './smear-api.service';
import { Trump } from './model/trump';

@Injectable()
export class HandService {
    private currentlyBidding: boolean;
    public showBidInput: boolean;
    public showTrumpInput: boolean;
    public allowBid: boolean;
    private cards: Card[];
    private selectedCard: Card;
    private allowSelection: boolean;
    private gameStatusMessage: string;
    private gameAndHand: GameAndHand;
    private gameAndUser: GameAndUser;
    private handMessage: string;
    private bidMessage: string;
    private bidInfo = new BidInfo(false, 0, "");
    private playingInfo: PlayingInfo;
    private handId: string;
    private trump: string;

    constructor(private smearApiService :SmearApiService) {
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.currentlyBidding = false;
        this.handMessage = "Waiting for cards...";
    }

    setGameInfo(gameAndUser: GameAndUser): void {
        this.gameAndUser = gameAndUser;
        this.allowSelection = false;
        this.showBidInput = false;
        this.showTrumpInput = false;
        this.allowBid = false;
        this.currentlyBidding = true;
        this.handMessage = "Waiting for cards...";
    }

    startNewHand(): void {
        this.setGameStatus("Waiting for cards to be dealt");
        this.getNewHand();
        this.allowBid = false;
        this.currentlyBidding = true;
    }

    getNewHand(): void {
        this.handMessage = "Waiting for cards...";
        this.smearApiService.handDeal(this.gameAndUser)
                            .subscribe( handInfo => this.receiveHand(handInfo),
                                        err => this.handleHandError(err, "Unable to retrieve cards"));
    }

    receiveHand(handInfo: HandInfo) {
        this.cards = handInfo.cards;
        this.handId = handInfo.hand_id;
        this.showBidInput = true;
        this.handMessage = "Your hand:";
        this.setGameStatus("Waiting for your turn to bid");
        this.getBidInfo();
    }

    getBidInfo(): void {
        this.smearApiService.handGetBidInfo(this.gameAndUser)
                            .subscribe( bidInfo => this.receiveBidInfo(bidInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information about bidding"));
    }

    receiveBidInfo(bidInfo: BidInfo) {
        this.bidInfo = bidInfo;
        this.allowBid = true;
        this.setGameStatus("Enter your bid below");
        if (this.bidInfo.current_bid < 2) {
            if (this.bidInfo.force_two) {
                this.setBidMessage("No one has bid yet. Since you are the dealer, if you pass you will take an automatic two set.");
            } else {
                this.setBidMessage("No one has bid yet");
            }
        } else {
            this.setBidMessage(this.bidInfo.bidder + " has the highest bid of " + this.bidInfo.current_bid);
        }
    }

    declareBid(bidNum: number): void {
        let bid = new Bid(this.gameAndUser.game_id, this.gameAndUser.username, bidNum);
        this.setGameStatus("Submitting bid");
        this.smearApiService.handSubmitBid(bid)
                            .subscribe( res => this.bidSubmitted(),
                                        err => this.handleHandError(err, "Unable to submit bid"));
    }

    bidSubmitted(): void {
        this.showBidInput = false;
        this.setGameStatus("Bid submitted successfully. Waiting to discover the high bidder");
        let gameAndHand = new GameAndHand(this.gameAndUser.game_id, this.handId);
        this.smearApiService.handGetHighBid(gameAndHand)
                            .subscribe( bid => this.highBidReceived(bid),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    highBidReceived(highBid: Bid): void {
        this.setGameStatus("High bid received: " + highBid.username + " bid: " + highBid.bid);
        if (highBid.bid == 0) {
            // Handle the case where bid == 0 - a forced two set
            this.setGameStatus("Dealer was forced to take a two set");
        } else if (highBid.username == this.gameAndUser.username) {
            this.setGameStatus("You are the bidder, enter your choice for trump below");
            this.showTrumpInput = true;
        } else {
            this.setGameStatus("Finding out what trump will be");
            this.getOrSubmitTrump("");
        }
    }

    submitTrump(trump: string): void {
        this.setGameStatus("Submitting trump to be " + trump);
        this.getOrSubmitTrump(trump);
    }

    getOrSubmitTrump(trump: string): void {
        let getTrump = new GetTrump(this.gameAndUser.game_id, this.gameAndUser.username, trump);
        this.smearApiService.handGetTrump(getTrump)
                            .subscribe( trump => this.trumpReceived(trump),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    trumpReceived(trump: Trump): void {
        this.trump = trump.trump;
        this.setGameStatus("Trump is " + this.trump + ", waiting for your turn");
        this.showTrumpInput = false;
        this.currentlyBidding = false;
        this.getPlayingInfo();
    }

    getPlayingInfo(): void {
        this.smearApiService.handGetPlayingInfo(this.gameAndUser)
                            .subscribe( playingInfo => this.receivePlayingInfo(playingInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information needed for playing"));
    }

    receivePlayingInfo(playingInfo: PlayingInfo) {
        this.allowSelections(true);
        this.playingInfo = playingInfo;
        this.setGameStatus("Trump is " + this.trump + ", pick a card to play");
    }

    handleHandError(err: any, message: string) {
        this.gameStatusMessage = message + <string>err;
        console.log(err);
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
            this.selectedCard = card;
        }
    }

    unSelectCard():void {
        this.selectedCard = undefined;
    }
    allowSelections(selections: boolean) {
        this.allowSelection = selections;
    }

    setGameStatus(message: string):void {
        this.gameStatusMessage = message;
    }

    getGameStatus(): string {
        return this.gameStatusMessage;
    }

    getHandMessage(): string {
        return this.handMessage;
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
