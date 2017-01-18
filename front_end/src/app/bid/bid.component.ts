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
    private trump: string;

    constructor(private handService: HandService) { }

    submit_bid() {
        console.log("bid submitted: " + this.bid);
        this.handService.declareBid(this.bid);
    }

    submit_trump() {
        console.log("trump submitted: " + this.trump);
        this.handService.submitTrump(this.trump);
    }

    ngOnInit() {
    }

}
