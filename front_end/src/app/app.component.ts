import { Angulartics2GoogleAnalytics } from 'angulartics2';
import { Component } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { SmearApiService } from './smear-api.service';


import { environment } from '../environments/environment';

import { GameService } from './game.service';

declare var ga: any;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'Play Smear';

  public email: string = '';
  public subject: string = '';
  public message: string = '';

  // This logic helps track page views using google analytics
  constructor(public smearApiService: SmearApiService, public router:Router, angulartics2GoogleAnalytics: Angulartics2GoogleAnalytics, public gameService: GameService) {}

  resetApp() {
    this.gameService.resetGame();
    this.router.navigate(['/start']);
  }

  sendContactUsEmail() {
    console.log('Sending email from: ' + this.email + ', with the subject: ' + this.subject + ', and the message: ' + this.message);
    this.smearApiService.sendContactUsEmail(this.email, this.subject, this.message).subscribe(
      res => res,
      err => console.log(err, 'Failed to send the email from ' + this.email + ', with the subject: ' + this.subject + ', and the message: ' + this.message)
    );
    this.resetContactUsData()
  }

  resetContactUsData() {
      this.email = '';
      this.subject = '';
      this.message = '';
  }
}
