import { Component, OnInit } from '@angular/core';
import { GameService } from '../game.service';

@Component({
  selector: 'app-join-game',
  templateUrl: './join-game.component.html',
  styleUrls: ['./join-game.component.css']
})
export class JoinGameComponent implements OnInit {

    constructor(public gameService: GameService) { }

    ngOnInit() { }

    gameJoinInputIsValid() {
        return !this.gameService.disableJoinButton && this.gameService.gameAndUser.game_id && this.gameService.gameAndUser.username;
    }

    joinGame() {
        this.gameService.joinGame();
    }

}
