import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';

function Player(props) {
  const {player} = props;
  return (
    <div style={{display: "inline-block", padding: 5}}>
      {player.name}
      <br />
      Team {player.team}
    </div>
  );
}

function PlayerDisplay(props) {
  const {players, teams} = props;
  const playerComponents = players.map((player, index) => (
    <Player player={player} key={index} />
  ))

  return (
    <div>
    {playerComponents}
    </div>
  );
}

export default withRouter(PlayerDisplay);
