import { Card } from './card';

export class PlayingInfo {
    constructor(
        public current_trick: Array<Card>,
        public current_winning_card: Card,
        public lead_suit: string) {
    }
}
