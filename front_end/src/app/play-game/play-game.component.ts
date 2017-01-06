import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';

import { BidComponent } from '../bid/bid.component';
import { Card } from '../common/card';
import { HandComponent } from '../hand/hand.component';
import { PlayHandComponent } from '../play-hand/play-hand.component';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-play-game',
  templateUrl: './play-game.component.html',
  styleUrls: ['./play-game.component.css']
})
export class PlayGameComponent implements OnInit {

    enterBid:boolean;
    initialCards: Observable<Card[]>;

    constructor(private smearApiService: SmearApiService) { 
        this.enterBid = true;
    }

    getInitialHand() {
        this.initialCards = this.smearApiService.getInitialHand();
    }

    sendBid(bid: number) {
        //this.smearApiService.sendBid(bid).then(cards => this.initialCards = cards);
    }

    receiveBid(bid:number):void {
        //Send bid to server using a service
        this.sendBid(bid);
        //Wait for first trick to come back
        this.enterBid = false;
    }

    receiveCardToPlay(card:number):void {
        //Update local hand
        //Send card to server using a service
        //Wait for next trick to come back, or end of game
    }
    ngOnInit() {
        // Use the gameID from the start page to ask for hand
        this.getInitialHand();
    }

}
