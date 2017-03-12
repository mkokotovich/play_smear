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
        // Add the Google Analytics javascript if running in production mode
        if (environment.production) {
            document.write('<script type="text/javascript">(function(i,s,o,g,r,a,m){i["GoogleAnalyticsObject"]=r;i[r]=i[r]||function(){ (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o), m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m) })(window,document,"script","https://www.google-analytics.com/analytics.js","ga"); ga("create", "UA-93535524-1", "auto"); </script>');

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
