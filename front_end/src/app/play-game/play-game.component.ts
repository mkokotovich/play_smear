import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { Router } from '@angular/router';

import { BidComponent } from '../bid/bid.component';
import { Card } from '../model/card';
import { HandComponent } from '../hand/hand.component';
import { HandService } from '../hand.service';
import { GameService } from '../game.service';
import { PlayHandComponent } from '../play-hand/play-hand.component';
import { GameId } from '../model/game-id';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-play-game',
  templateUrl: './play-game.component.html',
  styleUrls: ['./play-game.component.css']
})
export class PlayGameComponent implements OnInit {
    private gameId: GameId;

    constructor(private smearApiService: SmearApiService,
                private gameService: GameService,
                private router: Router,
                private handService: HandService) { 
    }

    ngOnInit() {
        // Redirect user back to start if they navigated here directly
        this.gameId = this.gameService.getGameId()
        if (this.gameId == undefined || this.gameId.game_id == "") {
            this.router.navigate(['/start']);
        }
        this.gameService.manageGame();
    }

}
