export class GameStartStatus {
    constructor(
        public ready: boolean,
        public num_players: number,
        public player_names: string[]) {
    }
}
