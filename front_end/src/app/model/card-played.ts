import { Card } from './card';

export class CardPlayed {
    constructor(
        public username: string,
        public card: Card) {
    }
}
