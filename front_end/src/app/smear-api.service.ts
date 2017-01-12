import { Injectable } from '@angular/core';
import { Headers, Http, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';

// Import RxJs required methods
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { Card } from './model/card';
import { GameId } from './model/game-id';
import { GameCreateInput } from './model/game-create-input';
import { GameAndUser } from './model/game-and-user';
import { GameStartStatusInput } from './model/game-start-status-input';
import { GameStartStatus } from './model/game-start-status';
import { CARDS } from './model/mock-cards';

@Injectable()
export class SmearApiService {
    private initialCardsUrl = 'api/getinitial';
    private serverAddress = "localhost:5000";
    private baseUrl = "http://" + this.serverAddress + '/api/';
    private gameCreateUrl = this.baseUrl + "game/create/";
    private gameJoinUrl = this.baseUrl + "game/join/";
    private gameStartStatusUrl = this.baseUrl + "game/startstatus/";
    private handDealUrl = this.baseUrl + "hand/deal/";

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

    getGameStartStatus(gameId: GameId): Observable<GameStartStatus> {
        let data = new GameStartStatusInput(gameId.game_id, true);
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.gameStartStatusUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    gameCreate(data: GameCreateInput): Observable<GameId> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.gameCreateUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    gameJoin(data: GameAndUser): Observable<GameId> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.gameJoinUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handDeal(data: GameAndUser): Observable<Array<Card>> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handDealUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    private extractData(res: Response) {
        let body = res.json();
        console.debug(body);
        return body.data || { };
    }

    private handleError (error: Response | any) {
        // In a real world app, we might use a remote logging infrastructure
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            const err = body.error || JSON.stringify(body);
            errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Observable.throw(errMsg);
    }
}
