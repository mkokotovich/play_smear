export class GameStartStatus {
    constructor(
        public ready: boolean,
        public num_players: number,
        public team_id: number,
        public player_names: string[]) {
    }
}
