import { Component, OnInit } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-play-hand',
  templateUrl: './play-hand.component.html',
  styleUrls: ['./play-hand.component.css']
})
export class PlayHandComponent implements OnInit {

    constructor(private handService: HandService) { }

    playSelectedCard() {
        console.log("play submitted: " + this.handService.getSelectedCard().value + " of " + this.handService.getSelectedCard().suit);
        // Send card to server
        // smearApiService.playSelectedCard(...);
        // Remove card from hand
        // Unselect, and reset for next card
        this.handService.unSelectCard();
        this.handService.allowSelections(true);
    }

    ngOnInit() {
    }

}
