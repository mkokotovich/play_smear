import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Button, Modal } from 'antd';
import axios from 'axios';

// import PlayerDisplay from './PlayerDisplay';
// import CardDisplay from './CardDisplay';
import TrumpHint from './TrumpHint';
import getErrorString from './utils';


function HUD(props) {
  const [autoPilot, setAutoPilot] = useState(false);
  const {game, loading, setLoading, signedInUser } = props;

  const myPlayer = game?.players.find(player => player.user === signedInUser.id)?.id || "unknown";
  const myTurnToPlay = game?.current_trick?.active_player === myPlayer;
  const myTurnToBid = game?.current_hand?.bidder === myPlayer && game.state === "bidding";

  function toggleAutoPilot() {
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/auto_pilot/`
    ).then((response) => {
      setLoading(false);
      setAutoPilot(!autoPilot);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to change AutoPilot setting",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  const trump = game?.current_hand?.trump;
  const plays = game?.current_trick?.plays || [];
  const leadCard = plays?.length !== 0 ? plays[0].card : "";
  const leadSuitLetter = leadCard.slice(1);
  const promptUserToPlay = (
    <>
      <div style={{color: "red", display: "flex", alignItems: "center"}}>
        &nbsp; &nbsp; <b>Your turn to play!</b>
      </div>
    </>
  );
  const promptUserToBid = (
    <>
      <div style={{color: "red", display: "flex", alignItems: "center"}}>
        &nbsp; &nbsp; <b>Your turn to bid!</b>
      </div>
    </>
  );

  return (
    <div style={{display: "flex-inline" }}>
      <div style={{display: "flex" }}>
        <Button onClick={toggleAutoPilot} disabled={loading}>{autoPilot ? "Disable" : "Enable"} AutoPilot</Button>
        { myTurnToPlay && promptUserToPlay }
        { myTurnToBid && promptUserToBid }
        <TrumpHint trump={trump} leadSuitLetter={leadSuitLetter} />
      </div>
      <hr />
    </div>
  );
}

export default withRouter(HUD);