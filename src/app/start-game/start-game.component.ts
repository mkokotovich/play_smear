import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-start-game',
  templateUrl: './start-game.component.html',
  styleUrls: ['./start-game.component.css']
})
export class StartGameComponent implements OnInit {
    numPlayers:number;

    startGame() {
        // Send numPlayers to server to start a game, retreive a gameID?
        this.router.navigate(['/play']);
    }
    constructor(private router: Router) { }

    ngOnInit() {
    }

}
