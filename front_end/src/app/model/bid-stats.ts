export class BidStats {
    constructor(
        public total_bids: number,
        public high_bids: number,
        public bids_won: number,
        public bids_set: number,
        public average_points_won: number,
        public average_points_lost: number) {
    }
}
