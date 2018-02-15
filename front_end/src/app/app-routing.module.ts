import { NgModule }      from '@angular/core';
import { RouterModule, Routes }   from '@angular/router';

import { StartGameComponent } from './start-game/start-game.component';
import { LobbyComponent } from './lobby/lobby.component';
import { PlayGameComponent } from './play-game/play-game.component';
import { HowToPlayComponent } from './how-to-play/how-to-play.component';
import { StatsComponent } from './stats/stats.component';

const routes: Routes = [
    { path: '', redirectTo: '/start', pathMatch: 'full' },
    { path: 'start',  component: StartGameComponent },
    { path: 'lobby', component: LobbyComponent },
    { path: 'play', component: PlayGameComponent },
    { path: 'rules', component: HowToPlayComponent },
    { path: 'stats', component: StatsComponent },
];
@NgModule({
    imports: [ RouterModule.forRoot(routes) ],
    exports: [ RouterModule ]
})
export class AppRoutingModule {}
