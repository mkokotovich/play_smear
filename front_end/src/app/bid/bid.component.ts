import { Component, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-bid',
  templateUrl: './bid.component.html',
  styleUrls: ['./bid.component.css']
})
export class BidComponent implements OnInit {

    @Output() notifyBid: EventEmitter<number> = new EventEmitter<number>();

    bid: number;

    submit_bid(event) {
        console.log("bid submitted: " + this.bid)
        this.notifyBid.emit(this.bid);
    }
    constructor() { }

    ngOnInit() {
    }

}
