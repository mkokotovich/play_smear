import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Row, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import HandResults from './HandResults';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function CardSelection(props) {
  const {cards, cardSelected, setCardSelected, submitSpecificCard} = props;

  function onChangeCardSelected(e) {
    submitSpecificCard(e.target.value);
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
  const [trickAcknowledged, setTrickAcknowledged] = useState(false);
  const {game, loading, setLoading, reloadGame, signedInUser} = props;
  const myPlayer = game.players.find(player => player.user === signedInUser.id)?.id;

  function submitSpecificCard(card) {
    //console.log(card);
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/hands/${game.current_hand.id}/tricks/${game.current_trick.id}/plays/`,
      { card: card }
    ).then((response) => {
      reloadGame(false, true, true);
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

  function submitCard() {
    return submitSpecificCard(cardSelected);
  }

  function nextTrick() {
    if (game.current_trick.num == 6) {
      setTrickAcknowledged(true);
    } else {
      reloadGame(true, true, true);
    }
  }

  const cardSelection = (
    <>
      <CardSelection cards={game.current_hand.cards} cardSelected={cardSelected} setCardSelected={setCardSelected} submitSpecificCard={submitSpecificCard} />
    </>
  );
  const player = game.players.find(player => player.id === game?.current_trick?.active_player);
  const waitingForTurn = (
    <>
      <p>Waiting for {player?.name} to play</p>
    </>
  );
  const taker = game.players.find(player => player.id === game.current_trick.taker);
  const trickFinishedPrompt = (
    <>
      <p>Trick is finished, {taker?.name} took the trick.</p>
      <Button onClick={nextTrick} disabled={loading}>Continue</Button>
    </>
  );
  const trickIsFinished = Boolean(game.current_trick.taker);
  const handIsFinished = Boolean(game.current_hand.results);
  const myTurn = game.current_trick.active_player === myPlayer;
  return (
    <div>
      <PlayerDisplay {...props} />
      { !trickIsFinished && <CardDisplay cards={game.current_hand.cards} /> }
      { myTurn && cardSelection }
      { !myTurn && !trickIsFinished && waitingForTurn }
      { !trickAcknowledged && trickIsFinished && trickFinishedPrompt }
      { trickAcknowledged && handIsFinished && <HandResults {...props} /> }
    </div>
  );
}

export default withRouter(Trick);
