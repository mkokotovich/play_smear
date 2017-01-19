import { Card } from './card';

export class GameUserCard {
    constructor(
        public game_id: string,
        public username: string,
        public card_to_play: Card) {
    }
}
