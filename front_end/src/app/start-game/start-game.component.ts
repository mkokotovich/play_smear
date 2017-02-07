import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { GameService } from '../game.service';
import { SmearApiService } from '../smear-api.service';
import { GameCreateInput } from '../model/game-create-input';
import { GameAndUser } from '../model/game-and-user';
import { GameStartStatus } from '../model/game-start-status';
import { GameId } from '../model/game-id';

@Component({
  selector: 'app-start-game',
  templateUrl: './start-game.component.html',
  styleUrls: ['./start-game.component.css']
})
export class StartGameComponent implements OnInit {
    private gameCreateInput = new GameCreateInput(0, 0);
    private gameAndUser = new GameAndUser("", "");
    private welcomeMessage = "";
    private errorMessage = "";
    private disableCreateButton = false;
    private disableJoinButton = false;
    private title = "Start or join a game";

    constructor(private router: Router,
                private gameService: GameService,
                private smearApiService: SmearApiService) { }

    gameCreateInputIsValid() {
        return !this.disableCreateButton && this.gameCreateInput.numPlayers;
    }

    gameJoinInputIsValid() {
        return !this.disableJoinButton && this.gameAndUser.game_id && this.gameAndUser.username;
    }

    createGame() {
        this.welcomeMessage = "Waiting for game to start..."
        this.errorMessage = "";
        this.disableCreateButton = true;
        // Send numPlayers to server to start a game, retreive a gameID?
        // Increment numHumanPlayers to account for self
        var numHumanPlayers = Number(this.gameCreateInput.numHumanPlayers) + 1
        this.gameCreateInput.numHumanPlayers = numHumanPlayers
        this.smearApiService.gameCreate(this.gameCreateInput)
                            .subscribe( gameId => this.gameIsCreated(gameId),
                                        err => this.handleStartError(err, "Unable to create game, make sure you have a valid number of players and try again"));

    }

    gameIsCreated(gameId: GameId) {
        this.gameAndUser.game_id = gameId.game_id;
        this.welcomeMessage = "Game " + this.gameAndUser.game_id + " created successfully!";
        if (this.gameCreateInput.numHumanPlayers != 0) {
            this.welcomeMessage += " Tell the other players to use game id " + this.gameAndUser.game_id + " and join the game!";
        }
    }

    joinGame() {
        this.welcomeMessage = "Joining game..."
        this.errorMessage = "";
        this.disableJoinButton = true;
        this.gameService.setGameInfo(this.gameAndUser.game_id, this.gameAndUser.username);
        this.smearApiService.gameJoin(this.gameAndUser)
                            .subscribe( gameId => this.checkGameStatus(gameId),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
    }

    checkGameStatus(gameId: GameId) {
        this.smearApiService.getGameStartStatus(gameId)
                            .subscribe( gameStartStatus => this.gameIsReady(gameStartStatus),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
    }

    gameIsReady(gameStartStatus: GameStartStatus) {
        this.gameService.setPlayers(gameStartStatus.num_players, gameStartStatus.player_names);
        this.router.navigate(['/play']);
    }

    handleStartError(err: any, message: string) {
        this.welcomeMessage = message;
        this.errorMessage = <any>err;
        console.log(err);
        this.disableCreateButton = false;
        this.disableJoinButton = false;
    }

    ngOnInit() {
    }

}
