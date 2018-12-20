import { PlayerTeam } from './player-team';

export class SetTeamParams {
    constructor(
        public game_id: string,
        public player_team_list: Array<PlayerTeam>) {
    }
}
