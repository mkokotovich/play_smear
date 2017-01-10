import { Injectable } from '@angular/core';
import { Headers, Http, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';

// Import RxJs required methods
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { Card } from './model/card';
import { GameId } from './model/game-id';
import { GameStartInput } from './model/game-start-input';
import { GameStartStatus } from './model/game-start-status';
import { CARDS } from './model/mock-cards';

@Injectable()
export class SmearApiService {
    private initialCardsUrl = 'api/getinitial';
    private serverAddress = "localhost:5000";
    private baseUrl = "http://" + this.serverAddress + '/api/';
    private gameStartUrl = this.baseUrl + "game/start/";
    private gameStartStatusBaseUrl = this.baseUrl + "game/startstatus/";

    constructor(private http: Http) { }

    getInitialHand(): Observable<Card[]> {
        //let initialHand$ = this.http.get(`${this.baseUrl}/gethand`, {headers: this.getHeaders()})
        //.map(mapCards);
        //return initialHand$
        return Observable.of(CARDS);
        //return this.http.get(this.initialCardsUrl)
        //.toPromise()
        //.then(response => response.json().data as Card[])
        //.catch(this.handleError);
    }

    getGameStartStatus(game_id: GameId): Observable<GameStartStatus> {
        return this.http.get(this.gameStartStatusBaseUrl + game_id.gameId)
                        .map((res:Response) => res.json())
                        .catch((error:any) => Observable.throw(error.json().error || 'Server error'));
    }

    gameStart(data: GameStartInput): Observable<GameId> {
        //let bodyString = JSON.stringify(data);
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.gameStartUrl, data, options)
                        .map((res:Response) => res.json())
                        .catch((error:any) => Observable.throw(error.json().error || 'Server error'));
    }

    private handleError(error: any): Promise<any> {
        console.error('An error occurred', error); // for demo purposes only
        return Promise.reject(error.message || error);
    }
}
