import React from 'react';
import { withRouter } from 'react-router-dom';
import { Button } from 'antd';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';

function GameResults(props) {
  const {game, loading, reloadGame} = props;

  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay cards={game.current_hand.cards} />
      Game Is Over
    </div>
  );
}

export default withRouter(GameResults);
