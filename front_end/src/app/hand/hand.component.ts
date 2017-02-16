import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Card } from '../model/card';
import { CardHelper } from '../card-helper';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-hand',
  templateUrl: './hand.component.html',
  styleUrls: ['./hand.component.css']
})
export class HandComponent implements OnInit {
    cardHelper = new CardHelper();

    constructor(private handService: HandService) { 
    }

    onSelect(card: Card):void {
        this.handService.selectCard(card);
    }

    ngOnInit() {
    }

}
