import { Angulartics2Module, Angulartics2GoogleAnalytics } from 'angulartics2';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { AlertModule } from 'ng2-bootstrap';
import { TabsModule } from 'ng2-bootstrap/tabs';
import { DndModule } from 'ng2-dnd';

//import { ButtonsModule } from 'ng2-bootstrap';

import { AppRoutingModule } from './app-routing.module';

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
import { HandStatusModalComponent } from './hand-status-modal/hand-status-modal.component';
import { CreateGameComponent } from './create-game/create-game.component';
import { JoinGameComponent } from './join-game/join-game.component';

@NgModule({
  declarations: [
    AppComponent,
    StartGameComponent,
    BidComponent,
    PlayHandComponent,
    PlayGameComponent,
    HandComponent,
    GameStatusComponent,
    HandStatusModalComponent,
    CreateGameComponent,
    JoinGameComponent
  ],
  imports: [
    AppRoutingModule,
    Angulartics2Module.forRoot([ Angulartics2GoogleAnalytics ]),
    BrowserModule,
    FormsModule,
    HttpModule,
    AlertModule.forRoot(),
    TabsModule.forRoot(),
    NgbModule.forRoot(),
    DndModule.forRoot()
  ],
  providers: [SmearApiService, HandService, GameService],
  entryComponents: [HandStatusModalComponent],
  bootstrap: [AppComponent]
})
export class AppModule { }
