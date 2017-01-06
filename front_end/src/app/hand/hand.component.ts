import { Component, OnInit, Input } from '@angular/core';
import { Card } from '../common/card';

@Component({
  selector: 'app-hand',
  templateUrl: './hand.component.html',
  styleUrls: ['./hand.component.css']
})
export class HandComponent implements OnInit {
    @Input()
    cards: Card[];
    selectedCard: Card;

    constructor() { }

    onSelect(card: Card):void {
        this.selectedCard = card;
    }

    ngOnInit() {
    }

}
