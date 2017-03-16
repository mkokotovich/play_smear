import { CardPlayed } from './card-played';

export class TrickResults {
    constructor(
        public cards_played: Array<CardPlayed>,
        public waiting_for: string,
        public trick_finished: boolean,
        public winner: string) {
    }
}
