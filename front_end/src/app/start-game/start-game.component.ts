import { Component, OnInit } from '@angular/core';

import { GameService } from '../game.service';

@Component({
  selector: 'app-start-game',
  templateUrl: './start-game.component.html',
  styleUrls: ['./start-game.component.css']
})
export class StartGameComponent implements OnInit {

    constructor(public gameService: GameService) { }


    ngOnInit() {
        this.gameService.loginUserFromCookie();
    }

}
