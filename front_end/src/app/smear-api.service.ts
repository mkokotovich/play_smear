import { Injectable } from '@angular/core';
import { Headers, Http, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';

// Import RxJs required methods
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { environment } from '../environments/environment';

import { AuthInfo } from './model/auth-info';
import { AuthResults } from './model/auth-results';
import { Bid } from './model/bid';
import { BidHint } from './model/bid-hint';
import { BidInfo } from './model/bid-info';
import { Card } from './model/card';
import { GameId } from './model/game-id';
import { GameCreateInput } from './model/game-create-input';
import { GameAndHand } from './model/game-and-hand';
import { GameAndUser } from './model/game-and-user';
import { GameJoinResults } from './model/game-join-results';
import { GameStartStatus } from './model/game-start-status';
import { GameUserCard } from './model/game-user-card';
import { GetTrump } from './model/get-trump';
import { HandInfo } from './model/hand-info';
import { HandResults } from './model/hand-results';
import { PlayerStats } from './model/player-stats';
import { PlayingInfo } from './model/playing-info';
import { SetTeamParams } from './model/set-team-params';
import { TrickResults } from './model/trick-results';
import { Trump } from './model/trump';
import { constants } from '../host-specific-constants';

@Injectable()
export class SmearApiService {
    private baseUrl = environment.apiBaseUrl + '/api/';
    private contactUsUrl = this.baseUrl + 'feedback/';
    private gameCreateUrl = this.baseUrl + "game/create/";
    private gameJoinUrl = this.baseUrl + "game/join/";
    private gameRejoinUrl = this.baseUrl + "game/rejoin/";
    private gameStartStatusUrl = this.baseUrl + "game/startstatus/";
    private gameStartUrl = this.baseUrl + "game/start/";
    private gameSetTeamsUrl = this.baseUrl + "game/setteams/";
    private handDealUrl = this.baseUrl + "hand/deal/";
    private handGetBidInfoUrl = this.baseUrl + "hand/getbidinfo/";
    private handSubmitBidUrl = this.baseUrl + "hand/submitbid/";
    private handGetHighBidUrl = this.baseUrl + "hand/gethighbid/";
    private handGetBidHintUrl = this.baseUrl + "hand/bidhint/";
    private handGetHintUrl = this.baseUrl + "hand/hint/";
    private handGetPlayingInfoUrl = this.baseUrl + "hand/getplayinginfo/";
    private handGetResultsUrl = this.baseUrl + "hand/getresults/";
    private handGetTrickResultsUrl = this.baseUrl + "hand/gettrickresults/";
    private handGetTrumpUrl = this.baseUrl + "hand/gettrump/";
    private handSubmitCardToPlayUrl = this.baseUrl + "hand/submitcard/";
    private userLoginUrl = this.baseUrl + "user/login/";
    private userLogoutUrl = this.baseUrl + "user/logout/";
    private userStatsUrl = this.baseUrl + "user/stats/";

    constructor(private http: Http) { }

    generateHTTPOptions(): RequestOptions {
        let headers = new Headers({ 'Content-Type': 'application/json' }); // ... Set content type to JSON
        let options = new RequestOptions({ withCredentials: true, headers: headers }); // Create a request option
        return options
    }

    loginUser(data: AuthInfo): Observable<AuthResults> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.userLoginUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                          return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    logoutUser(): Observable<AuthResults> {
        let options = this.generateHTTPOptions();
        let data = null;

        return this.http.post(this.userLogoutUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    getGameStartStatus(data: GameAndUser): Observable<GameStartStatus> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameStartStatusUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    gameCreate(data: GameCreateInput): Observable<GameId> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameCreateUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    gameJoin(data: GameAndUser): Observable<GameJoinResults> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameJoinUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    gameRejoin(data: GameAndUser): Observable<GameJoinResults> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameRejoinUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    gameStart(data: GameId): Observable<any> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameStartUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    gameSetTeams(data: SetTeamParams): Observable<any> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.gameSetTeamsUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handDeal(data: GameAndUser): Observable<HandInfo> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handDealUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetBidInfo(data: GameAndUser): Observable<BidInfo> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetBidInfoUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handSubmitBid(data: Bid): Observable<any> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handSubmitBidUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetHighBid(data: GameAndHand): Observable<BidInfo> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetHighBidUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetTrump(data: GetTrump): Observable<Trump> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetTrumpUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetPlayingInfo(data: GameAndUser): Observable<PlayingInfo> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetPlayingInfoUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handSubmitCardToPlay(data: GameUserCard): Observable<any> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handSubmitCardToPlayUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetTrickResults(data: GameAndUser): Observable<TrickResults> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetTrickResultsUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    handGetResults(data: GameAndHand): Observable<HandResults> {
        let options = this.generateHTTPOptions();

        return this.http.post(this.handGetResultsUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

    getPlayerStats(): Observable<PlayerStats> {
        let options = this.generateHTTPOptions();
        let data = null;

        return this.http.post(this.userStatsUrl, data, options)
                        .map(this.extractData)
                        .retryWhen((error) => {
                            return this.handleErrorRetry(error);
                        })
                        .catch(this.handleError);
    }

  sendContactUsEmail(email: string, subject: string, body: string): Observable<any> {
    let options = this.generateHTTPOptions();
    let data: any = {'email': email, 'subject': subject, 'body': body};

    return this.http
      .post(this.contactUsUrl, data, options)
      .map(this.extractData)
      .retryWhen((error) => {
        return this.handleErrorRetry(error);
      })
      .catch(this.handleError);
  }

  handGetHint(data: GameAndUser): Observable<Card> {
    let options = this.generateHTTPOptions();

    return this.http
      .post(this.handGetHintUrl, data, options)
      .map(this.extractData)
      .retryWhen((error) => {
        return this.handleErrorRetry(error);
      })
      .catch(this.handleError);
  }

  handGetBidHint(data: GameAndUser): Observable<BidHint> {
    let options = this.generateHTTPOptions();

    return this.http
      .post(this.handGetBidHintUrl, data, options)
      .map(this.extractData)
      .retryWhen((error) => {
        return this.handleErrorRetry(error);
      })
      .catch(this.handleError);
  }

    private extractData(res: Response) {
        let body = res.json();
        console.debug(body);
        return body.data || { };
    }

    private handleErrorRetry(errors: Observable<any>): Observable<any> {
        return errors
                .mergeMap((error) => (error.status === 503) ? Observable.of(error) : Observable.throw(error))
                .delay(2000)
                .take(600);
    }

    private handleError (error: Response | any) {
        return Observable.throw(error.json().error || 'Unknown server error');
    }
}
