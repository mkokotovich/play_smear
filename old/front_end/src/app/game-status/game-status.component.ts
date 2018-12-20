import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { CardHelper } from '../card-helper';
import { GameService } from '../game.service';
import { HandService } from '../hand.service';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-game-status',
  templateUrl: './game-status.component.html',
  styleUrls: ['./game-status.component.css']
})
export class GameStatusComponent implements OnInit {
    //Local copy just for easy of use
    private numPlayers: number;
    public cardHelper = new CardHelper();

    constructor(public handService: HandService,
                public gameService: GameService,
                public router: Router,
                public smearApiService: SmearApiService) {
    }

    ngOnInit() {
        this.numPlayers = this.gameService.getNumPlayers();
    }

    playAgain() {
        this.gameService.resetGame();
        this.router.navigate(['/start']);
    }
}
