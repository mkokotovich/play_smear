import React from 'react';

function Bid(props) {
  const {bid, isDealer, isBidder, currentlyBidding} = props;
  const bidMessageWhileBidding = !bid ? " " : bid?.bid === 0 ? "Passed" : `Bid ${bid?.bid}`;
  const bidMessageAfterBidding = isBidder ? `Bidder, bid ${bid?.bid}` : bidMessageWhileBidding;
  const bidMessage = currentlyBidding ? bidMessageWhileBidding : bidMessageAfterBidding;
  return (
    <div>
      {isDealer && currentlyBidding && <b>Dealer</b>}
      <p>{ bidMessage }</p>
    </div>
  );
}

export default Bid;
