export class GameJoinResults {
    constructor(
        public game_id: string,
        public username: string,
        public num_teams: number,
        public points_to_play_to: number,
        public graph_prefix: string) {
    }
}
