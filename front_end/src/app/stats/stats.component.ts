import { Component, OnInit } from '@angular/core';

import { GameService } from '../game.service';

@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css']
})
export class StatsComponent implements OnInit {

    constructor(public gameService: GameService) { }

    ngOnInit() {
    }

}

