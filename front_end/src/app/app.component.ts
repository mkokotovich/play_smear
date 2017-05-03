import { Angulartics2GoogleAnalytics } from 'angulartics2';
import { Component } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';

import { environment } from '../environments/environment';

declare var ga: any;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
    title = 'Play Smear';

    // This logic helps track page views using google analytics
    constructor(router:Router, angulartics2GoogleAnalytics: Angulartics2GoogleAnalytics) {
    }
}
