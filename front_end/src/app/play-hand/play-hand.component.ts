import { Component, OnInit } from '@angular/core';

import { Card } from '../model/card';
import { HandService } from '../hand.service';
import { HandStatusModalComponent } from '../hand-status-modal/hand-status-modal.component';

@Component({
  selector: 'app-play-hand',
  templateUrl: './play-hand.component.html',
  styleUrls: ['./play-hand.component.css']
})
export class PlayHandComponent implements OnInit {

    constructor(private handService: HandService) {
    }

    open() {
    }

    playSelectedCard() {
        console.log("play submitted: " + this.handService.getSelectedCard().value + " of " + this.handService.getSelectedCard().suit);
        this.handService.submitCardToPlay(this.handService.getSelectedCard());
    }

    ngOnInit() {
    }

}
