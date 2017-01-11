import { Injectable } from '@angular/core';

import { Player } from './model/player';

@Injectable()
export class GameService {

    private numPlayers: number;
    private players: Player[];
    private username: string;
    private gameId: string;

    constructor() { }

    setGameInfo(gameId: string, username: string):void {
        this.gameId = gameId;
        this.username = username;
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

    getNumPlayers(): number {
        return this.numPlayers;
    }
}
