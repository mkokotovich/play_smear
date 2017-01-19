import { CardPlayed } from './card-played';

export class TrickResults {
    constructor(
        public winner: string,
        public cards_played: Array<CardPlayed>) {
    }
}
