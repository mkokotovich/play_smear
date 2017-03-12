import { Component } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
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
    constructor(router:Router) {
        // Send pageview to Google Analytics if running in production mode
        if (environment.production) {
            // Using Rx's built in `distinctUntilChanged ` feature to handle url change
            router.events.distinctUntilChanged((previous: any, current: any) => {
                // Subscribe to any `NavigationEnd` events where the url has changed
                if(current instanceof NavigationEnd) {
                    return previous.url === current.url;
                }
                return true;
            }).subscribe((x: any) => {
                ga('set', 'page', x.url);
                ga('send', 'pageview')
            });
        }
    }
}
