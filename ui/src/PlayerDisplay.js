import React, { useState, useEffect } from 'react';
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
      } = {},
      teams = [],
    } = {}
  } = props;
  const bid = bids.find(bid => bid.player === player.id);
  const play = plays.find(play => play.player === player.id);
  const card = play ? play.card : undefined;
  const teamName = teams ? teams.find(team => team.id === player.team).name : "";
  const isDealer = dealer === player.id;
  const isBidder = bidder === player.id;
  const isActivePlayer = active_player === player.id;
  const waitingForMe = (currentlyBidding && isBidder) || (!currentlyBidding && isActivePlayer);


  const border = waitingForMe ? "3px solid blue" : "1px solid grey";
  const playerStyles = {
    display: "inline-block",
    padding: 15,
    margin: 5,
    border: border,
    borderRadius: "5px",
    height: "100%",
  };

  return (
    <div style={playerStyles}>
      <p>
        {player.name}
      </p>
      {player.team && (<p> {teamName} </p>)}
      {<Bid bid={bid} isDealer={isDealer} currentlyBidding={currentlyBidding} isBidder={isBidder}/>}
      {card && <Card card={card} />}
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
