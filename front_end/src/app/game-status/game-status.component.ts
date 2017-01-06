import { Component, OnInit } from '@angular/core';

import { HandService } from '../hand.service';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-game-status',
  templateUrl: './game-status.component.html',
  styleUrls: ['./game-status.component.css']
})
export class GameStatusComponent implements OnInit {

    constructor(private handService: HandService,
                private smearApiService: SmearApiService) {
    }

    ngOnInit() {
    }

}
