import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-bid',
  templateUrl: './bid.component.html',
  styleUrls: ['./bid.component.css']
})
export class BidComponent implements OnInit {
    public bid = 0;

    private trumpChoices = [ "Spades", "Clubs", "Hearts", "Diamonds" ];

    constructor(private handService: HandService) {
        this.bid = 0;
    }

    get_bid(): string {
        let bid_str = ""
        if (this.bid == 0) {
            bid_str = "Pass";
        } else {
            bid_str = this.bid.toString();
        }

        return bid_str;
    }

    save_bid(bid: number) {
        this.bid = bid;
    }

    submit_bid() {
        console.log("bid submitted: " + this.bid);
        this.handService.declareBid(this.bid);
    }

    submit_trump(trump: string) {
        console.log("trump submitted: " + trump);
        this.handService.submitTrump(trump);
    }

    ngOnInit() {
    }

}
