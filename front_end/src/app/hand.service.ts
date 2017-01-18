import { Injectable } from '@angular/core';

import { Bid} from './model/bid';
import { BidInfo } from './model/bid-info';
import { Card } from './model/card';
import { GameAndUser } from './model/game-and-user';
import { GameId } from './model/game-id';
import { SmearApiService } from './smear-api.service';

@Injectable()
export class HandService {
    private bidding: boolean;
    public allowBid: boolean;
    private cards: Card[];
    private selectedCard: Card;
    private allowSelection: boolean;
    private gameStatusMessage: string;
    private gameAndUser: GameAndUser;
    private handMessage: string;
    private bidMessage: string;
    private bidInfo = new BidInfo(false, 0, "");

    constructor(private smearApiService :SmearApiService) {
        this.allowSelection = false;
        this.bidding = true;
        this.allowBid = false;
        this.handMessage = "Waiting for cards...";
    }

    setGameInfo(gameAndUser: GameAndUser): void {
        this.gameAndUser = gameAndUser;
        this.allowSelection = false;
        this.bidding = true;
        this.allowBid = false;
        this.handMessage = "Waiting for cards...";
    }


    declareBid(bidNum: number): void {
        let bid = new Bid(this.gameAndUser.game_id, this.gameAndUser.username, bidNum);
        this.setGameStatus("Submitting bid");
        this.smearApiService.handSubmitBid(bid)
                            .subscribe( res => this.bidSubmitted(),
                                        err => this.handleHandError(err, "Unable to submit bid"));
        this.bidding = false;
    }

    bidSubmitted(): void {
        this.setGameStatus("Bid submitted successfully. Waiting to discover the high bidder");
        let gameId = new GameId(this.gameAndUser.game_id);
        this.smearApiService.handGetHighBid(gameId)
                            .subscribe( bid => this.highBidReceived(bid),
                                        err => this.handleHandError(err, "Unable to get the high bidder"));
    }

    highBidReceived(highBid: Bid): void {
        this.setGameStatus("High bid received: " + highBid.username + " bid: " + highBid.bid);
    }

    isBidding(): boolean {
        return this.bidding;
    }
  
    startNewHand(): void {
        this.setGameStatus("Waiting for cards to be dealt");
        this.getNewHand();
        this.allowBid = false;
    }

    getNewHand(): void {
        this.handMessage = "Waiting for cards...";
        this.smearApiService.handDeal(this.gameAndUser)
                            .subscribe( cards => this.receiveHand(cards),
                                        err => this.handleHandError(err, "Unable to retrieve cards"));
    }

    receiveHand(cards: Card[]) {
        this.cards = cards;
        this.handMessage = "Your hand:";
        this.setGameStatus("Waiting for your turn to bid");
        this.getBidInfo();
    }

    getBidInfo(): void {
        this.smearApiService.handGetBidInfo(this.gameAndUser)
                            .subscribe( bidInfo => this.receiveBidInfo(bidInfo),
                                        err => this.handleHandError(err, "Unable to retrieve information about biddin"));
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
}
