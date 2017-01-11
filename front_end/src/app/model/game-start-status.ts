export class GameStartStatus {
    constructor(
        public ready: boolean,
        public numPlayers: number,
        public players: string[]) {
    }
}
