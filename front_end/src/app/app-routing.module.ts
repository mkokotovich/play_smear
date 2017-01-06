import { NgModule }      from '@angular/core';
import { RouterModule, Routes }   from '@angular/router';

import { StartGameComponent } from './start-game/start-game.component';
import { PlayGameComponent } from './play-game/play-game.component';

const routes: Routes = [
    { path: '', redirectTo: '/start', pathMatch: 'full' },
    { path: 'start',  component: StartGameComponent },
    { path: 'play', component: PlayGameComponent },
];
@NgModule({
    imports: [ RouterModule.forRoot(routes) ],
    exports: [ RouterModule ]
})
export class AppRoutingModule {}
