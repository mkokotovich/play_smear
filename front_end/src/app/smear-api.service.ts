import { Injectable } from '@angular/core';
import { Headers, Http, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';

// Import RxJs required methods
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { Bid } from './model/bid';
import { BidInfo } from './model/bid-info';
import { Card } from './model/card';
import { GameId } from './model/game-id';
import { GameCreateInput } from './model/game-create-input';
import { GameAndHand } from './model/game-and-hand';
import { GameAndUser } from './model/game-and-user';
import { GameStartStatusInput } from './model/game-start-status-input';
import { GameStartStatus } from './model/game-start-status';
import { GameUserCard } from './model/game-user-card';
import { GetTrump } from './model/get-trump';
import { HandInfo } from './model/hand-info';
import { HandResults } from './model/hand-results';
import { PlayingInfo } from './model/playing-info';
import { TrickResults } from './model/trick-results';
import { Trump } from './model/trump';

@Injectable()
export class SmearApiService {
    private initialCardsUrl = 'api/getinitial';
    private serverAddress = "localhost:5000";
    //private serverAddress = "192.168.86.200:5000";
    private baseUrl = "http://" + this.serverAddress + '/api/';
    private gameCreateUrl = this.baseUrl + "game/create/";
    private gameJoinUrl = this.baseUrl + "game/join/";
    private gameStartStatusUrl = this.baseUrl + "game/startstatus/";
    private handDealUrl = this.baseUrl + "hand/deal/";
    private handGetBidInfoUrl = this.baseUrl + "hand/getbidinfo/";
    private handSubmitBidUrl = this.baseUrl + "hand/submitbid/";
    private handGetHighBidUrl = this.baseUrl + "hand/gethighbid/";
    private handGetPlayingInfoUrl = this.baseUrl + "hand/getplayinginfo/";
    private handGetResultsUrl = this.baseUrl + "hand/getresults/";
    private handGetTrickResultsUrl = this.baseUrl + "hand/gettrickresults/";
    private handGetTrumpUrl = this.baseUrl + "hand/gettrump/";
    private handSubmitCardToPlayUrl = this.baseUrl + "hand/submitcard/";

    constructor(private http: Http) { }

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

    handDeal(data: GameAndUser): Observable<HandInfo> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handDealUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetBidInfo(data: GameAndUser): Observable<BidInfo> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetBidInfoUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handSubmitBid(data: Bid): Observable<any> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handSubmitBidUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetHighBid(data: GameAndHand): Observable<BidInfo> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetHighBidUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetTrump(data: GetTrump): Observable<Trump> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetTrumpUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetPlayingInfo(data: GameAndUser): Observable<PlayingInfo> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetPlayingInfoUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handSubmitCardToPlay(data: GameUserCard): Observable<any> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handSubmitCardToPlayUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetTrickResults(data: GameAndUser): Observable<TrickResults> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetTrickResultsUrl, data, options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    handGetResults(data: GameAndHand): Observable<HandResults> {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ headers: headers }); // Create a request option

        return this.http.post(this.handGetResultsUrl, data, options)
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
