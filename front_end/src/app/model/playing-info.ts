import { Card } from './card';
import { CardPlayed } from './card-played';

export class PlayingInfo {
    constructor(
        public cards_played: Array<CardPlayed>,
        public current_winning_card: Card,
        public lead_suit: string) {
    }
}
