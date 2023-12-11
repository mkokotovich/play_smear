import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function BidInput(props) {
  const {game, highBid, twoSet, bidValue, setBidValue} = props;

  function onChangeBid(e) {
    setBidValue(e.target.value);
  }

  const passText = twoSet ? "Accept 2 set" : "Pass";
  return (
    <>
      <p>What is your bid:</p>
      <RadioGroup name="bidValue" onChange={onChangeBid} value={bidValue}>
        <RadioButton value="0">{passText}</RadioButton>
        <RadioButton disabled={highBid >= 2} value="2">2</RadioButton>
        <RadioButton disabled={highBid >= 3} value="3">3</RadioButton>
        <RadioButton disabled={highBid >= 4} value="4">4</RadioButton>
        <RadioButton disabled={highBid >= 5} value="5">5</RadioButton>
      </RadioGroup>
    </>
  );
}

function Bidding(props) {
  const [bidValue, setBidValue] = useState("0");
  const {game, loading, setLoading, reloadGame, signedInUser} = props;
  const myPlayer = game.players.find(player => player.user === signedInUser.id)?.id;
  const myTurn = game?.current_hand?.bidder === myPlayer;

  function submitBid() {
    console.log(bidValue);
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/hands/${game.current_hand.id}/bids/`,
      { bid: bidValue }
    ).then((response) => {
      reloadGame(false, true, true);
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

  const player = game.players.find(player => player.id === game?.current_hand?.bidder);
  const waitingForTurn = (
    <>
      <p>Waiting for {player?.name} to bid</p>
    </>
  );
  const highBidId = game?.current_hand?.high_bid;
  const highBid = game?.current_hand?.bids.find(bid => bid.id === highBidId)?.bid;
  const amIDealer = game?.current_hand?.dealer === myPlayer;
  const bidInput = (
    <>
      <BidInput game={game} highBid={highBid} twoSet={amIDealer && highBid  === 0} bidValue={bidValue} setBidValue={setBidValue} />
      &nbsp;
      <Button onClick={submitBid} disabled={loading}>Submit Bid</Button>
    </>
  );

  return (
    <div>
      <PlayerDisplay {...props} />
      <CardDisplay {...props} />
      { !myTurn && waitingForTurn }
      { myTurn && bidInput }
    </div>
  );
}

export default withRouter(Bidding);
