import { Angulartics2Module } from 'angulartics2';
import { Angulartics2GoogleAnalytics } from 'angulartics2/ga';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { AlertModule } from 'ngx-bootstrap/alert';
import { TabsModule } from 'ngx-bootstrap/tabs';
import { ModalModule } from 'ngx-bootstrap/modal';
import { DndModule } from 'ng2-dnd';

import { AppRoutingModule } from './app-routing.module';

import { AlertService } from './alert.service';
import { AppComponent } from './app.component';
import { BidComponent } from './bid/bid.component';
import { GameService } from './game.service';
import { HandComponent } from './hand/hand.component';
import { HandService } from './hand.service';
import { PlayHandComponent } from './play-hand/play-hand.component';
import { PlayGameComponent } from './play-game/play-game.component';
import { SmearApiService } from './smear-api.service';
import { StartGameComponent } from './start-game/start-game.component';
import { GameStatusComponent } from './game-status/game-status.component';
import { CreateGameComponent } from './create-game/create-game.component';
import { JoinGameComponent } from './join-game/join-game.component';
import { ScoreboardComponent } from './scoreboard/scoreboard.component';
import { HowToPlayComponent } from './how-to-play/how-to-play.component';
import { GraphViewerComponent } from './graph-viewer/graph-viewer.component';
import { GraphLoaderComponent } from './graph-loader/graph-loader.component';
import { StatsComponent } from './stats/stats.component';

@NgModule({
  declarations: [
    AppComponent,
    StartGameComponent,
    BidComponent,
    PlayHandComponent,
    PlayGameComponent,
    HandComponent,
    GameStatusComponent,
    CreateGameComponent,
    JoinGameComponent,
    ScoreboardComponent,
    HowToPlayComponent,
    GraphViewerComponent,
    GraphLoaderComponent,
    StatsComponent
  ],
  imports: [
    AppRoutingModule,
    Angulartics2Module.forRoot([ Angulartics2GoogleAnalytics ]),
    BrowserModule,
    FormsModule,
    HttpModule,
    AlertModule.forRoot(),
    TabsModule.forRoot(),
    ModalModule.forRoot(),
    DndModule.forRoot()
  ],
  providers: [SmearApiService, HandService, GameService, AlertService],
  entryComponents: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
