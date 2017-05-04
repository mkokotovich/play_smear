import { Component, Input, OnInit } from '@angular/core';

import { GameService } from '../game.service';

@Component({
  selector: 'app-create-game',
  templateUrl: './create-game.component.html',
  styleUrls: ['./create-game.component.css']
})
export class CreateGameComponent implements OnInit {
    public numPlayers: number = 1;
    public pointsToPlayTo: number = 11;
    public numHumanPlayers: number = 0;
    public numComputerPlayers: number = 0;

    @Input()
    public playAgainstPeople: boolean = false;

    constructor(public gameService: GameService) { }

    ngOnInit() {
    }

    gameCreateInputIsValid() {
        return !this.gameService.disableCreateButton &&
            this.numPlayers > 1 &&
            this.gameService.gameAndUser.username;
    }

    gameJoinInputIsValid() {
        return !this.gameService.disableJoinButton && this.gameService.gameAndUser.game_id && this.gameService.gameAndUser.username;
    }

    minHumanPlayersReached() {
        return this.numHumanPlayers <= 0;
    }

    maxHumanPlayersReached() {
        return (this.numHumanPlayers + this.numComputerPlayers) >= 7;
    }

    minComputerPlayersReached() {
        return this.numComputerPlayers <= 0;
    }

    maxComputerPlayersReached() {
        return (this.numHumanPlayers + this.numComputerPlayers) >= 7;
    }

    setPoints(points: number) {
        this.gameService.pointsToPlayTo = points;
    }

    setNumTeams(teams: number) {
        this.gameService.numTeams = teams;
    }

    changePlayers(humans:boolean, increment:boolean) {
        if (humans) {
            if (increment) {
                this.numHumanPlayers += 1;
            } else {
                this.numHumanPlayers -= 1;
            }
        } else {
            if (increment) {
                this.numComputerPlayers += 1;
            } else {
                this.numComputerPlayers -= 1;
            }
        }
        this.numPlayers = 1 + this.numHumanPlayers + this.numComputerPlayers;
    }

    createAndJoinGame() {
        if (this.playAgainstPeople == false) {
            // Make sure that the user didn't set this and then hide it.
            this.gameService.gameCreateInput.numHumanPlayers = 0;
        } else {
            this.gameService.gameCreateInput.numHumanPlayers = this.numHumanPlayers;
        }
        this.gameService.gameCreateInput.numPlayers = 1 + this.numHumanPlayers + this.numComputerPlayers;
        this.gameService.createAndJoinGame();
    }
}
