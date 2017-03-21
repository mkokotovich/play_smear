export class GameCreateInput {
    constructor(
        public numHumanPlayers: number,
        public numPlayers: number,
        public pointsToPlayTo: number) {
    }
}
