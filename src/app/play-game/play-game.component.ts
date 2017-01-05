import { Component, OnInit } from '@angular/core';

import { BidComponent } from '../bid/bid.component';
import { PlayHandComponent } from '../play-hand/play-hand.component';

@Component({
  selector: 'app-play-game',
  templateUrl: './play-game.component.html',
  styleUrls: ['./play-game.component.css']
})
export class PlayGameComponent implements OnInit {

    displayHand:boolean;

    constructor() { 
        this.displayHand = false;
    }

    receiveBid(bid:number):void {
        //Send bid to server using a service
        //Wait for first trick to come back
        this.displayHand = true;
    }

    receiveCardToPlay(card:number):void {
        //Update local hand
        //Send card to server using a service
        //Wait for next trick to come back, or end of game
        this.displayHand = true;
    }
    ngOnInit() {
    }

}
