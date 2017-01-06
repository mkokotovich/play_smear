import { Injectable } from '@angular/core';

import { Player } from './common/player';

@Injectable()
export class GameService {

    private numPlayers: number;
    private players: Player[];

    constructor() { }

    setNumPlayers(numPlayers: number):void {
        this.numPlayers = numPlayers;
        this.players = new Array<Player>();
        this.players.push(new Player("you", true));
        for (var i = 1; i < this.numPlayers; i++) {
            this.players.push(new Player("player"+i, false));
        }
    }

    getPlayers(): Player[] {
        return this.players;
    }

    getNumPlayers(): number {
        return this.numPlayers;
    }
}
