import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';
import { CardHelper } from '../card-helper';


@Component({
  selector: 'app-bid',
  templateUrl: './bid.component.html',
  styleUrls: ['./bid.component.css']
})
export class BidComponent implements OnInit {
    public cardHelper = new CardHelper();

    private trumpChoices = [ "Spades", "Clubs", "Hearts", "Diamonds" ];

    constructor(public handService: HandService) {
    }

    get_bid(): string {
        let bid_str = ""
        if (this.handService.bid == 0) {
            bid_str = "Pass";
        } else {
            bid_str = this.handService.bid.toString();
        }

        return bid_str;
    }

    save_bid(bid: number) {
        this.handService.bid = bid;
    }

    submit_bid() {
        console.log("bid submitted: " + this.handService.bid);
        this.handService.declareBid(this.handService.bid);
    }

    save_trump(trump: string) {
        this.handService.bidTrump = trump;
    }

    submit_trump() {
        console.log("trump submitted: " + this.handService.bidTrump);
        this.handService.submitTrump(this.handService.bidTrump);
    }

    get_trump(): string {
        return this.handService.bidTrump;
    }

    ngOnInit() {
    }

}
