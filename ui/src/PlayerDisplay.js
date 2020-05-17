import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import Card from './Card';
import Bid from './Bid';

function Player(props) {
  const {
    player,
    game: {
      current_trick: {
        plays = []
      } = {},
      current_hand: {
        bids = []
      } = {},
    } = {}
  } = props;
  const bid = bids.find(bid => bid.player === player.id);
  const play = plays.find(play => play.player === player.id);
  const card = play ? play.card : "";

  return (
    <div style={{display: "inline-block", padding: 15}}>
      {player.name}
      <br />
      Team {player.team}
      <br />
      <Bid bid={bid} />
      <br />
      <Card card={card} />
    </div>
  );
}

function PlayerDisplay(props) {
  const { game: { players = [] } = {} } = props;
  const playerComponents = players.map((player, index) => (
    <Player player={player} key={index} {...props} />
  ));

  return (
    <div>
    {playerComponents}
    </div>
  );
}

export default withRouter(PlayerDisplay);
