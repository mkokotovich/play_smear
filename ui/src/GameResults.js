import React from 'react';
import { withRouter } from 'react-router-dom';
// import { Button } from 'antd';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';

function GameResults(props) {
  // eslint-disable-next-line no-unused-vars
  const {game, loading, reloadGame} = props;

  const winners = game.players.filter(player => player.winner);
  const winner_names = winners.map(player => player.name);
  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay cards={game.current_hand.cards} />
      Game is over, <b>{winner_names.toString()}</b> won! <span style={{fontSize: "40px"}}>🏆</span>
    </div>
  );
}

export default withRouter(GameResults);
