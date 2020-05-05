import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Row, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import ActionButton from './ActionButton';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function BidInput(props) {
  const {bidValue, setBidValue} = props;

  function onChangeBid(e) {
    setBidValue(e.target.value);
  }

  return (
    <>
      <p>What is your bid:</p>
      <RadioGroup name="bidValue" onChange={onChangeBid} value={bidValue}>
        <RadioButton value="0">Pass</RadioButton>
        <RadioButton value="2">2</RadioButton>
        <RadioButton value="3">3</RadioButton>
        <RadioButton value="4">4</RadioButton>
        <RadioButton value="5">5</RadioButton>
      </RadioGroup>
    </>
  );
}

function Bidding(props) {
  const [bidValue, setBidValue] = useState("0");
  const {game, loading, setLoading, reloadGame} = props;

  function submitBid() {
    console.log(bidValue);
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/hands/${game.current_hand.id}/bids/`,
      { bid: bidValue }
    ).then((response) => {
      reloadGame(true, true, true);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to submit bid",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay cards={game.current_hand.cards} />
      <BidInput bidValue={bidValue} setBidValue={setBidValue} />
      &nbsp;
      <Button onClick={submitBid} disabled={loading}>Submit Bid</Button>
    </div>
  );
}

export default withRouter(Bidding);
