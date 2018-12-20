import { Component, OnInit } from '@angular/core';

import { environment } from '../../environments/environment';
import { HandService } from '../hand.service';

@Component({
  selector: 'app-graph-loader',
  templateUrl: './graph-loader.component.html',
  styleUrls: ['./graph-loader.component.css']
})
export class GraphLoaderComponent implements OnInit {

    private staticBaseUrl = environment.apiBaseUrl + '/static/';

    public getCurrentFilename() {
        var handId = "1";
        if (this.handService.handId) {
            handId = this.handService.handId;
        }
        if (this.handService.enableNextHandButton) {
            // This means we should look for the next hand id, rather than the current one
            handId = (parseInt(handId, 10) + 1).toString()
        }
        if (this.handService.handResults && this.handService.handResults.is_game_over) {
            handId = "final";
        }
        return this.handService.graphPrefix + "_hand" + handId + ".png";
    }

    public getGraphUrl() {
        return this.staticBaseUrl + this.getCurrentFilename();
    }

    constructor(public handService: HandService) {
    }

    ngOnInit() {
    }

}
