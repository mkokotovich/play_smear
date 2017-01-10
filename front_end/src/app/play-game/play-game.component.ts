import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';

import { BidComponent } from '../bid/bid.component';
import { Card } from '../model/card';
import { HandComponent } from '../hand/hand.component';
import { HandService } from '../hand.service';
import { PlayHandComponent } from '../play-hand/play-hand.component';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-play-game',
  templateUrl: './play-game.component.html',
  styleUrls: ['./play-game.component.css']
})
export class PlayGameComponent implements OnInit {

    constructor(private smearApiService: SmearApiService,
                private handService: HandService) { 
    }

    getInitialHand() {
        this.handService.getInitialHand();
    }

    ngOnInit() {
        // Use the gameID from the start page to ask for hand
        this.handService.setGameStatus("Waiting for cards to be dealt");
        this.getInitialHand();
        this.handService.setGameStatus("Waiting for bids");
    }

}
