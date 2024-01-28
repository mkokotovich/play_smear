import React, { useState } from 'react';
import { Redirect, withRouter } from 'react-router-dom';
// import { Button } from 'antd';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import ActionButton from './ActionButton';
import CreateGame from './CreateGame';

function GameResults(props) {
  // eslint-disable-next-line no-unused-vars
  const {game, loading, reloadGame} = props;
  const [goHome, setGoHome] = useState(false);

  const teams = game.num_teams > 0;
  const winners = teams ? game.teams.filter(team => team.winner) : game.players.filter(player => player.winner);
  const winner_names = winners.map(winner => winner.name);

  function newGameClick() {
    setGoHome(true);
  }

  if (goHome) {
    return <Redirect push to="/" />
  }

  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay cards={game.current_hand.cards} />
      Game is over, <b>{winner_names.toString()}</b> won! <span style={{fontSize: "40px"}}>🏆</span>
      <CreateGame single={game.single_player} signedIn={true} buttonText="Start another game"/>
      <ActionButton buttonText="Home" handleClick={() => newGameClick()} />
    </div>
  );
}

export default withRouter(GameResults);
