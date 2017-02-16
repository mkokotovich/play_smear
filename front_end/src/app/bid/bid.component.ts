import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-bid',
  templateUrl: './bid.component.html',
  styleUrls: ['./bid.component.css']
})
export class BidComponent implements OnInit {
    private trumpChoices = [ "Spades", "Clubs", "Hearts", "Diamonds" ];

    constructor(private handService: HandService) {
    }

    submit_bid(bid: number) {
        console.log("bid submitted: " + bid);
        this.handService.declareBid(bid);
    }

    submit_bid_as_pass() {
        console.log("pass submitted");
        this.handService.declareBid(0);
    }

    submit_trump(trump: string) {
        console.log("trump submitted: " + trump);
        this.handService.submitTrump(trump);
    }

    ngOnInit() {
    }

}
