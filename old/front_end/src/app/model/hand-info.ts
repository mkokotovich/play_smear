import { Card } from './card';

export class HandInfo {
    constructor(
        public cards: Array<Card>,
        public hand_id: string) {
    }
}
