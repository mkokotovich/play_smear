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
    private title = "Start or join a game";

    constructor(private router: Router,
                private gameService: GameService,
                private smearApiService: SmearApiService) { }

    gameCreateInputIsValid() {
        return !this.gameService.disableCreateButton && this.gameService.gameCreateInput.numPlayers;
    }

    gameJoinInputIsValid() {
        return !this.gameService.disableJoinButton && this.gameService.gameAndUser.game_id && this.gameService.gameAndUser.username;
    }

    createGame() {
        this.gameService.createGame();
    }

    joinGame() {
        this.gameService.joinGame();
    }

    ngOnInit() {
    }

}
