import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import Card from './Card';

function Player(props) {
  const { player, game: { current_trick: { plays = [] } = {} } = {} } = props;
  const play = plays.find(play => play.player === player.id);
  const card = play ? play.card : "";

  return (
    <div style={{display: "inline-block", padding: 15}}>
      {player.name}
      <br />
      Team {player.team}
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
