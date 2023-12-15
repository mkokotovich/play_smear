import React from 'react';
import { withRouter } from 'react-router-dom';
import { Button } from 'antd';

function HandResults(props) {
  // eslint-disable-next-line no-unused-vars
  const {game, loading, reloadGame, resetCards, setCards} = props;

  function nextHand(bidder, bid, points_won) {
    window.analytics.track("Hand Ended", {
      "Bidder User ID": bidder.user,
      "Bidder Name": bidder.name,
      "Bidder is_computer": bidder.is_computer,
      "Bid": bid,
      "Points Won": points_won,
      "Bid ID": game?.current_hand?.high_bid,
      "Hand ID": game?.current_hand?.id,
      "Game ID": game?.id,
      "Game Num Players": game?.num_players,
      "Game Num Teams": game?.num_teams,
    });
    if (resetCards) {
      setCards([]);
    }
    reloadGame(true, true, true);
  }

  const bidder = game.players.find(player => player.id === game?.current_hand?.bidder);
  const bidders = bidder.team ? game.players.filter(player => player.team === bidder.team) : [bidder];
  const bidderIds = bidders.map(player => player.id);
  const high_bid = game?.current_hand?.bids.find(bid => bid.id === game?.current_hand?.high_bid);
  var bidder_points = 0;
  for (const [point, winner_id] of Object.entries(game?.current_hand?.results)) {
    if (bidderIds.indexOf(winner_id) !== -1) {
      bidder_points += 1;
    }
  }
  const dealerTookTwoSetReaction = (<>{bidder.name} was dealer and took a two set! <span style={{fontSize: "40px"}}>👎</span></>);
  const madeBidReaction = (<>{bidder.name} made the bid! <span style={{fontSize: "40px"}}>👍</span></>);
  const wasSetReaction = (<>{bidder.name} was set! <span style={{fontSize: "40px"}}>👎</span></>);

  const dealerTookTwoSet = high_bid.bid === 0;
  const madeBid = !dealerTookTwoSet && bidder_points >= high_bid.bid;
  const bidReaction = madeBid ? madeBidReaction : (
    dealerTookTwoSet ? dealerTookTwoSetReaction : wasSetReaction
  );

  return (
    <div>
      Hand Is Over! {bidder.name} bid {high_bid.bid} and got {bidder_points}. {bidReaction}
      <br />
      <Button onClick={()=>nextHand(bidder, high_bid.bid, bidder_points)} disabled={loading}>Continue</Button>
    </div>
  );
}

export default withRouter(HandResults);
