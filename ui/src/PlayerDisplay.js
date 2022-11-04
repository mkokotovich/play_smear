import React from 'react';
import { withRouter } from 'react-router-dom';
import Card from './Card';
import Bid from './Bid';

function Player(props) {
  const {
    player,
    currentlyBidding,
    game: {
      current_trick: {
        plays = [],
        active_player = undefined,
      } = {},
      current_hand: {
        bids = [],
        dealer,
        bidder,
        results = {},
      } = {},
      teams = [],
    } = {}
  } = props;
  const bid = bids.find(bid => bid.player === player.id);
  const play = plays.find(play => play.player === player.id);
  const card = play ? play.card : undefined;
  const team = teams.find(team => team.id === player.team);
  const teamName = team?.name || "";
  const isDealer = dealer === player.id;
  const isBidder = bidder === player.id;
  const isActivePlayer = active_player === player.id;
  const waitingForMe = (currentlyBidding && isBidder) || (!currentlyBidding && isActivePlayer);

  const possiblePoints = results ? Object.keys(results) : [];
  
  const pointsWon = possiblePoints.reduce((accum, key) => {
    if (results[key] === player.id) {
      return [...accum, key]
    }
    return accum
  }, []);
  const pointToHumanText = {
    "winner_high": "Won High",
    "winner_low": "Won Low",
    "winner_game": "Won Game",
    "winner_jick": "Won Jick",
    "winner_jack": "Won Jack"
  };
  const resultsEntries = pointsWon.map((point) => {
    return (
      <div>
        <b>{pointToHumanText[point]}</b>
      </div>
    );
  });;

  const border = waitingForMe ? "4px solid blue" : "1px solid grey";
  const playerStyles = {
    display: "flex-inline",
    alignSelf: "flex-start",
    alignItems: "center",
    padding: 10,
    margin: 5,
    border: border,
    borderRadius: "5px",
    minWidth: "130px",
    maxWidth: "200px",
    height: "100%",
  };
  const score = team ? team.score : player.score;

  return (
    <div style={playerStyles}>
      {player.name}<br/>
      {player.team && (<> {teamName} <br/></>)}
      Score: {score}
      {<Bid bid={bid} isDealer={isDealer} currentlyBidding={currentlyBidding} isBidder={isBidder}/>}
      {card && <Card card={card} small={true}/>}
      {results && (<> Game Points: {player.current_hand_game_points_won} </>) }
      {results && resultsEntries}
    </div>
  );
}

function PlayerDisplay(props) {
  const { game: { players = [], state } = {} } = props;
  const playerComponents = players.map((player, index) => (
    <Player player={player} currentlyBidding={state === "bidding"} key={index} {...props} />
  ));

  return (
    <div style={{display: "flex"}}>
      {playerComponents}
    </div>
  );
}

export default withRouter(PlayerDisplay);
