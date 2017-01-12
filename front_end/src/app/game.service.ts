import { Injectable } from '@angular/core';

import { Player } from './model/player';
import { GameId } from './model/game-id';
import { GameAndUser } from './model/game-and-user';

@Injectable()
export class GameService {

    private numPlayers: number;
    private players: Player[];
    private username: string;
    private gameId: GameId;
    private gameAndUser = new GameAndUser("", "");

    constructor() { }

    setGameInfo(gameId: string, username: string):void {
        this.gameId = new GameId(gameId);
        this.gameAndUser.game_id = gameId;
        this.gameAndUser.username = username;
    }

    setPlayers(numPlayers: number, playerList: string[]):void {
        this.numPlayers = numPlayers;
        this.players = new Array<Player>();
        for (var i = 0; i < this.numPlayers; i++) {
            this.players.push(new Player(playerList[i], 0, this.username == playerList[i]));
        }
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
