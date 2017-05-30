import { Component, OnInit } from '@angular/core';

import { environment } from '../../environments/environment';

@Component({
  selector: 'app-graph-loader',
  templateUrl: './graph-loader.component.html',
  styleUrls: ['./graph-loader.component.css']
})
export class GraphLoaderComponent implements OnInit {

  private staticBaseUrl = environment.apiBaseUrl + '/static';

  constructor() { }

  ngOnInit() {
  }

}
