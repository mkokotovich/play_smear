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
    public playAgainstPeople: boolean;

    constructor(private router: Router,
                private gameService: GameService,
                private smearApiService: SmearApiService) {
        this.playAgainstPeople = false;
    }

    gameCreateInputIsValid() {
        return !this.gameService.disableCreateButton &&
            this.gameService.gameCreateInput.numPlayers &&
            this.gameService.gameAndUser.username;
    }

    gameJoinInputIsValid() {
        return !this.gameService.disableJoinButton && this.gameService.gameAndUser.game_id && this.gameService.gameAndUser.username;
    }

    createAndJoinGame() {
        if (this.playAgainstPeople == false) {
            // Make sure that the user didn't set this and then hide it.
            this.gameService.gameCreateInput.numHumanPlayers = 0;
        }
        this.gameService.createAndJoinGame();
    }

    joinGame() {
        this.gameService.joinGame();
    }

    ngOnInit() {
    }

}
