export class BidStats {
    constructor(
        public games_played: number,
        public games_won: number,
        public games_lost: number,
        public total_bids: number,
        public high_bids: number,
        public bids_won: number,
        public bids_set: number,
        public average_points_won: number,
        public average_points_lost: number) {
    }
}
