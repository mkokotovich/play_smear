import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Row, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function CardSelection(props) {
  const {cards, cardSelected, setCardSelected} = props;

  function onChangeCardSelected(e) {
    setCardSelected(e.target.value);
  }

  const cardRadios = cards.map((card, idx) => (
    <RadioButton value={card} key={idx}>{card}</RadioButton>
  ));

  return (
    <>
      <p>Which card do you want to play</p>
      <RadioGroup name="cardSelected" onChange={onChangeCardSelected} value={cardSelected}>
        {cardRadios}
      </RadioGroup>
    </>
  );
}

function Trick(props) {
  const [cardSelected, setCardSelected] = useState();
  const {game, loading, setLoading, reloadGame, signedInUser} = props;
  const myPlayer = game.players.find(player => player.user === signedInUser.id)?.id

  function submitCard() {
    console.log(cardSelected);
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/hands/${game.current_hand.id}/tricks/${game.current_trick.id}/plays/`,
      { card: cardSelected }
    ).then((response) => {
      reloadGame(true, true, true);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to submit card to play",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  const cardSelection = (
    <>
      <CardSelection cards={game.current_hand.cards} cardSelected={cardSelected} setCardSelected={setCardSelected} />
      &nbsp;
      <Button onClick={submitCard} disabled={loading}>Submit Card</Button>
    </>
  );
  const player = game.players.find(player => player.id === game?.current_trick?.active_player);
  const waitingForTurn = (
    <>
      <p>Waiting for {player?.name} to play</p>
    </>
  );
  const selectOrWait = game?.current_trick?.active_player === myPlayer ? cardSelection : waitingForTurn;
  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay cards={game.current_hand.cards} />
      {selectOrWait}
    </div>
  );
}

export default withRouter(Trick);
