import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { GameService } from '../game.service';
import { SmearApiService } from '../smear-api.service';
import { GameStartInput } from '../model/game-start-input';
import { GameStartStatus } from '../model/game-start-status';
import { GameId } from '../model/game-id';

@Component({
  selector: 'app-start-game',
  templateUrl: './start-game.component.html',
  styleUrls: ['./start-game.component.css']
})
export class StartGameComponent implements OnInit {
    private gameStartInput = new GameStartInput(0, "");
    private welcomeMessage = "Enter your username and the desired number of players (2-8) below";
    private disableButton = false;
    private title = "Start a new game";
    private gameId = new GameId("");
    private gameStartStatus = new GameStartStatus(false, []);

    constructor(private router: Router,
                private gameService: GameService,
                private smearApiService: SmearApiService) { }

    gameStartInputIsValid() {
        return !this.disableButton && this.gameStartInput.numPlayers && this.gameStartInput.username;
    }

    startGame() {
        this.disableButton = true;
        this.welcomeMessage = "Waiting for game to begin"
        // Send numPlayers to server to start a game, retreive a gameID?
        this.smearApiService.gameStart(this.gameStartInput)
                            .subscribe( gameId => this.gameId = gameId,
                                       err => { console.log(err); });

        //while (this.gameId.gameId == "") {
        //}

        this.smearApiService.getGameStartStatus(this.gameId)
        .subscribe( gameStartStatus => this.gameStartStatus = gameStartStatus,
                   err => { console.log(err); });
        //while (this.gameStartStatus.ready == false) {
        //}
        this.gameService.setNumPlayers(this.gameStartInput.numPlayers);
        //this.router.navigate(['/play']);
    }

    ngOnInit() {
    }

}
