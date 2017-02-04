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
    private selectedTrump: string;
    private trumpChoices = [ "Spades", "Clubs", "Hearts", "Diamonds" ];

    constructor(private handService: HandService) {
        this.bid = 0;
    }

    submit_bid() {
        console.log("bid submitted: " + this.bid);
        this.handService.declareBid(this.bid);
    }

    submit_bid_as_pass() {
        console.log("pass submitted");
        this.handService.declareBid(0);
    }

    submit_trump() {
        console.log("trump submitted: " + this.selectedTrump);
        this.handService.submitTrump(this.selectedTrump);
    }

    ngOnInit() {
    }

}
