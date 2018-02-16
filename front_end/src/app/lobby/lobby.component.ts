import { Component, OnInit } from '@angular/core';

import { GameService } from '../game.service';

@Component({
  selector: 'app-lobby',
  templateUrl: './lobby.component.html',
  styleUrls: ['./lobby.component.css']
})
export class LobbyComponent implements OnInit {

    constructor(public gameService: GameService) {}

    ngOnInit() {
        // Attempt to rejoin a game if navigated here without a gameID set
        var gameId = this.gameService.getGameId()
        if (gameId == undefined || gameId.game_id == "") {
            return this.gameService.rejoinGame();
        }
    }

}
