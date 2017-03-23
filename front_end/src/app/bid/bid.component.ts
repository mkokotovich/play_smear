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
    public bid:number;
    public selected_trump:string;
    public cardHelper = new CardHelper();

    private trumpChoices = [ "Spades", "Clubs", "Hearts", "Diamonds" ];

    constructor(private handService: HandService) {
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

    save_trump(trump: string) {
        this.selected_trump = trump;
    }

    submit_trump() {
        console.log("trump submitted: " + this.selected_trump);
        this.handService.submitTrump(this.selected_trump);
    }

    get_trump(): string {
        return this.selected_trump;
    }

    ngOnInit() {
    }

}
