export class GameJoinResults {
    constructor(
        public game_id: string,
        public username: string,
        public team_id: number,
        public num_teams: number,
        public points_to_play_to: number) {
    }
}
