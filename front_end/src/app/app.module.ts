import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

//import { AlertModule } from 'ng2-bootstrap';
//import { ButtonsModule } from 'ng2-bootstrap';

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';
import { BidComponent } from './bid/bid.component';
import { HandComponent } from './hand/hand.component';
import { HandService } from './hand.service';
import { PlayHandComponent } from './play-hand/play-hand.component';
import { PlayGameComponent } from './play-game/play-game.component';
import { SmearApiService } from './smear-api.service';
import { StartGameComponent } from './start-game/start-game.component';

@NgModule({
  declarations: [
    AppComponent,
    StartGameComponent,
    BidComponent,
    PlayHandComponent,
    PlayGameComponent,
    HandComponent
  ],
  imports: [
    AppRoutingModule,
    BrowserModule,
    FormsModule,
    HttpModule
  ],
  providers: [SmearApiService, HandService],
  bootstrap: [AppComponent]
})
export class AppModule { }
