import { Component, OnInit } from '@angular/core';

import { CardHelper } from '../card-helper';
import { GameService } from '../game.service';
import { HandService } from '../hand.service';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-scoreboard',
  templateUrl: './scoreboard.component.html',
  styleUrls: ['./scoreboard.component.css']
})
export class ScoreboardComponent implements OnInit {

    //Local copy just for easy of use
    private numPlayers: number;
    public cardHelper = new CardHelper();

    constructor(private handService: HandService,
                private gameService: GameService,
                private smearApiService: SmearApiService) {
    }

    ngOnInit() {
        this.numPlayers = this.gameService.getNumPlayers();
    }

}
