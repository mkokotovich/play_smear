import { Bid } from './bid';

export class BidInfo {
    constructor(
        public force_two: boolean,
        public current_bid: number,
        public bidder: string,
        public all_bids: Array<Bid>) {
    }
}
