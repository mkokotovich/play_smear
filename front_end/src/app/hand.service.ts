import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Rx';

import { SmearApiService } from './smear-api.service';
import { Card } from './common/card';

@Injectable()
export class HandService {
    private bidding: boolean;
    private cards: Observable<Card[]>;
    private selectedCard: Card;
    private allowSelection: boolean;

    constructor(private smearApiService :SmearApiService) {
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
        this.cards = this.smearApiService.getInitialHand();
    }

    getCards(): Observable<Card[]> {
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

}
