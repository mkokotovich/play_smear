import { Component, OnInit } from '@angular/core';
import { Card } from '../common/card';
import { CARDS } from '../common/mock-cards';

@Component({
  selector: 'app-hand',
  templateUrl: './hand.component.html',
  styleUrls: ['./hand.component.css']
})
export class HandComponent implements OnInit {
    cards: Card[];

    constructor(cards: Card[]) {
        this.cards = cards;
    }

    ngOnInit() {
    }

}
