import React from 'react';
import { withRouter } from 'react-router-dom';
import { Button } from 'antd';

function HandResults(props) {
  const {game, loading, reloadGame} = props;

  function nextHand() {
    reloadGame(true, true, true);
  }

  return (
    <div>
      Hand Is Over
      <br />
      <Button onClick={nextHand} disabled={loading}>Continue</Button>
    </div>
  );
}

export default withRouter(HandResults);
