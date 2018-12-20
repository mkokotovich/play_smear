import { Bid } from './bid';

export class BidInfo {
    constructor(
        public all_bids: Array<Bid>,
        public waiting_for: string,
        public dealer: string,
        public ready: boolean,
        public force_two: boolean,
        public current_bid: number,
        public bidder: string) {
    }
}
