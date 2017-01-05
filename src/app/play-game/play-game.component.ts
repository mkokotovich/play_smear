import { Component, OnInit } from '@angular/core';

import { BidComponent } from '../bid/bid.component';
import { Card } from '../common/card';
import { CARDS } from '../common/mock-cards';
import { HandComponent } from '../hand/hand.component';
import { PlayHandComponent } from '../play-hand/play-hand.component';

@Component({
  selector: 'app-play-game',
  templateUrl: './play-game.component.html',
  styleUrls: ['./play-game.component.css']
})
export class PlayGameComponent implements OnInit {

    enterBid:boolean;
    hand: HandComponent;

    constructor() { 
        this.enterBid = true;
    }

    getInitialHand() {
        this.hand = new HandComponent(CARDS);
    }

    receiveBid(bid:number):void {
        //Send bid to server using a service
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
