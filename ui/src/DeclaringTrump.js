import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function TrumpInput(props) {
  const {trump, setTrump} = props;

  function onChangeTrump(e) {
    setTrump(e.target.value);
  }

  return (
    <>
      <p>Pick a suit for trump</p>
      <RadioGroup name="trump" onChange={onChangeTrump} value={trump}>
        <RadioButton value="spades">Spades</RadioButton>
        <RadioButton value="hearts">Hearts</RadioButton>
        <RadioButton value="clubs">Clubs</RadioButton>
        <RadioButton value="diamonds">Diamonds</RadioButton>
      </RadioGroup>
    </>
  );
}

function DeclaringTrump(props) {
  const [trump, setTrump] = useState();
  const {game, loading, setLoading, reloadGame, signedInUser} = props;
  const myPlayer = game.players.find(player => player.user === signedInUser.id)?.id;
  const myTurn = game.current_hand.bidder === myPlayer;

  function submitTrump() {
    console.log(trump);
    setLoading(true);
    axios.patch(`/api/smear/v1/games/${game.id}/hands/${game.current_hand.id}/bids/${game.current_hand.high_bid}/`,
      { trump: trump }
    ).then((response) => {
      reloadGame(true, true, true);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to submit trump",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  const submitTrumpDialog = (
    <>
      <TrumpInput trump={trump} setTrump={setTrump} />
      &nbsp;
      <Button onClick={submitTrump} disabled={loading}>Submit Trump</Button>
    </>
  );
  const player = game.players.find(player => player.id === game?.current_hand?.bidder);
  const waitingForTurn = (
    <>
      <p>Waiting for {player?.name} to declare trump</p>
    </>
  );

  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay {...props} />
      { myTurn && submitTrumpDialog }
      { !myTurn && waitingForTurn }
    </div>
  );
}

export default withRouter(DeclaringTrump);
