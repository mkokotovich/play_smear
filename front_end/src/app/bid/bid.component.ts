import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-bid',
  templateUrl: './bid.component.html',
  styleUrls: ['./bid.component.css']
})
export class BidComponent implements OnInit {
    private bid: number;

    constructor(private handService: HandService) { }

    submit_bid() {
        console.log("bid submitted: " + this.bid);
        this.handService.declareBid(this.bid);
        this.handService.allowSelections(true);
        this.handService.setGameStatus("Waiting for cards to be played");
    }

    ngOnInit() {
    }

}
