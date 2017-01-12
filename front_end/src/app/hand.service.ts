import { Injectable } from '@angular/core';

import { SmearApiService } from './smear-api.service';
import { GameService } from './game.service';
import { Card } from './model/card';

@Injectable()
export class HandService {
    private bidding: boolean;
    private cards: Card[];
    private selectedCard: Card;
    private allowSelection: boolean;
    private gameStatusMessage: string;

    constructor(private smearApiService :SmearApiService,
                private gameService: GameService) {
        this.allowSelection = false;
        this.bidding = true;
    }

    declareBid(bid: number): void {
        //this.smearApiService.sendBid(bid).then(cards => this.hand = cards);
        this.bidding = false;
    }

    isBidding(): boolean {
        return this.bidding;
    }
  
    getInitialHand(): void {
        this.smearApiService.handDeal(this.gameService.getGameAndUser())
                            .subscribe( cards => this.cards = cards,
                                        err => this.handleHandError(err, "Unable to retrieve cards"));
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
}
