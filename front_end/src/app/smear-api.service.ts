import { Injectable } from '@angular/core';
import { Headers, Http, Response } from '@angular/http';
import { Observable } from 'rxjs/Rx';

import { Card } from './common/card';
import { CARDS } from './common/mock-cards';

@Injectable()
export class SmearApiService {
    private initialCardsUrl = 'api/getinitial';

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

    private handleError(error: any): Promise<any> {
        console.error('An error occurred', error); // for demo purposes only
        return Promise.reject(error.message || error);
    }
}
