import { Cookie } from 'ng2-cookies/ng2-cookies';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { Player } from './model/player';
import { GameId } from './model/game-id';
import { GameAndUser } from './model/game-and-user';
import { GameCreateInput } from './model/game-create-input';
import { GameStartStatus } from './model/game-start-status';
import { HandService } from './hand.service';
import { SmearApiService } from './smear-api.service';

@Injectable()
export class GameService {

    public gameCreateInput = new GameCreateInput(0, 0);
    public gameAndUser = new GameAndUser("", "");
    private welcomeMessage = "";
    private errorMessage = "";
    public disableCreateButton = false;
    public disableJoinButton = false;
    private numPlayers: number;
    private players: Player[];
    private username: string;
    private gameId: GameId;

    constructor(private router: Router,
                private handService: HandService,
                private smearApiService: SmearApiService) { }

    manageGame() {
        this.handService.startNewHand();
    }

    createGame() {
        this.welcomeMessage = "Waiting for game to start...";
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

    rejoinGame() {
        this.gameAndUser.game_id = Cookie.get("game_id");
        this.gameAndUser.username = Cookie.get("username");
        if (this.gameAndUser.game_id == undefined || this.gameAndUser.game_id == "") {
            return this.unableToJoin("An existing game could not be found");
        }
        this.welcomeMessage = "Attempting to rejoin a previous game...";
        this.errorMessage = "";
        this.disableJoinButton = true;
        this.setGameInfo(this.gameAndUser.game_id, this.gameAndUser.username);
        this.smearApiService.gameRejoin(this.gameAndUser)
                            .subscribe( gameAndUser => this.checkGameStatus(gameAndUser),
                                        err => this.unableToJoin(err));
    }

    unableToJoin(err: any) {
        this.welcomeMessage = "Unable to join any existing games, create or join a game to play";
        this.errorMessage = <any>err;
        this.disableJoinButton = false;
        this.router.navigate(['/start']);
    }

    joinGame() {
        Cookie.deleteAll();
        this.welcomeMessage = "Joining game..."
        this.errorMessage = "";
        this.disableJoinButton = true;
        this.setGameInfo(this.gameAndUser.game_id, this.gameAndUser.username);
        this.smearApiService.gameJoin(this.gameAndUser)
                            .subscribe( gameAndUser => this.checkGameStatus(gameAndUser),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
    }

    checkGameStatus(gameAndUser: GameAndUser) {
        this.setGameInfo(gameAndUser.game_id, gameAndUser.username);
        this.saveGameInfoInCookie();
        this.smearApiService.getGameStartStatus(new GameId(gameAndUser.game_id))
                            .subscribe( gameStartStatus => this.gameIsReady(gameStartStatus),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
    }

    gameIsReady(gameStartStatus: GameStartStatus) {
        this.setPlayers(gameStartStatus.num_players, gameStartStatus.player_names);
        this.router.navigate(['/play']);
        this.manageGame();
    }

    handleStartError(err: any, message: string) {
        this.welcomeMessage = message;
        this.errorMessage = <any>err;
        console.log(err);
        this.disableCreateButton = false;
        this.disableJoinButton = false;
    }


    //Also reset all globals
    setGameInfo(gameId: string, username: string):void {
        this.gameId = new GameId(gameId);
        this.handService.setGameInfo(this.gameAndUser);
    }

    saveGameInfoInCookie() {
        Cookie.set('game_id', this.gameAndUser.game_id, 1 /*days from now*/);
        Cookie.set('username', this.gameAndUser.username, 1 /*days from now*/);
    }

    setPlayers(numPlayers: number, playerList: string[]):void {
        this.numPlayers = numPlayers;
        this.players = new Array<Player>();
        for (var i = 0; i < this.numPlayers; i++) {
            this.players.push(new Player(playerList[i], 0, new Array<string>(), this.username == playerList[i]));
        }
        this.handService.setPlayers(this.players);
    }

    getPlayers(): Player[] {
        return this.players;
    }

    getGameAndUser(): GameAndUser {
        return this.gameAndUser;
    }

    getGameId(): GameId {
        return this.gameId;
    }

    getNumPlayers(): number {
        return this.numPlayers;
    }
}
