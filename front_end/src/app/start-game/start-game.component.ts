import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { GameService } from '../game.service';
import { SmearApiService } from '../smear-api.service';

@Component({
  selector: 'app-start-game',
  templateUrl: './start-game.component.html',
  styleUrls: ['./start-game.component.css']
})
export class StartGameComponent implements OnInit {
    private numPlayers:number;

    constructor(private router: Router,
                private gameService: GameService,
                private smearApiService: SmearApiService) { }

    startGame() {
        this.gameService.setNumPlayers(this.numPlayers);
        // Send numPlayers to server to start a game, retreive a gameID?
        //this.smearApiService.startGame(this.numPlayers);
        this.router.navigate(['/play']);
    }

    ngOnInit() {
    }

}
