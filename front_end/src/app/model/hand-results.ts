import { PlayerInfo } from './model/player-info';

export class HandResults {
    constructor(
        public high_winner: string,
        public low_winner: string,
        public jack_winner: string,
        public jick_winner: string,
        public game_winner: string,
        public bidder_set: boolean,
        public is_game_over: boolean,
        public player_infos: Array<PlayerInfo>) {
    }
}
