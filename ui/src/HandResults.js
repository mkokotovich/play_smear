import React from 'react';
import { withRouter } from 'react-router-dom';
import { Button } from 'antd';

function HandResults(props) {
  // eslint-disable-next-line no-unused-vars
  const {game, loading, reloadGame} = props;

  function nextHand() {
    reloadGame(true, true, true);
  }

  const bidder = game.players.find(player => player.id === game?.current_hand?.bidder);
  const high_bid = game?.current_hand?.bids.find(bid => bid.id === game?.current_hand?.high_bid);
  var bidder_points = 0;
  for (const [point, winner_id] of Object.entries(game?.current_hand?.results)) {
    if (winner_id === bidder.id) {
      bidder_points += 1;
    }
  }

  return (
    <div>
      Hand Is Over! {bidder.name} bid {high_bid.bid} and got {bidder_points}.
      <br />
      <Button onClick={nextHand} disabled={loading}>Continue</Button>
    </div>
  );
}

export default withRouter(HandResults);
