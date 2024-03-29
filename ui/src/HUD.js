import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Button, Modal } from 'antd';
import axios from 'axios';

// import PlayerDisplay from './PlayerDisplay';
// import CardDisplay from './CardDisplay';
import TrumpHint from './TrumpHint';
import ScoreGraph from './ScoreGraph';
import getErrorString from './utils';


function HUD(props) {
  const {game, loading, setLoading, signedInUser } = props;

  const myPlayer = game?.players.find(player => player.user === signedInUser.id);
  const autoPilotEnabled = myPlayer?.is_computer;
  const [autoPilot, setAutoPilot] = useState(autoPilotEnabled);
  const [scoreGraphVisible, setScoreGraphVisible] = useState(false);
  const myTurnToPlay = game?.current_trick?.active_player === myPlayer?.id;
  const myTurnToBid = game?.current_hand?.bidder === myPlayer?.id && game?.state === "bidding";

  React.useEffect(() => {
    const myPlayer = game?.players.find(player => player.user === signedInUser.id);
    const autoPilotEnabled = myPlayer?.is_computer;
    setAutoPilot(autoPilotEnabled);
  }, [game])

  function showScoreGraph() {
    setScoreGraphVisible(true);
  }

  function toggleAutoPilot() {
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/auto_pilot/`
    ).then((response) => {
      setLoading(false);
      setAutoPilot(autoPilotEnabled);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      setAutoPilot(autoPilotEnabled);
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
      <div style={{fontSize: "1.5em", color: "red", display: "flex", alignItems: "center"}}>
        &nbsp; &nbsp; <b>Your turn to play!</b>
      </div>
    </>
  );
  const promptUserToBid = (
    <>
      <div style={{fontSize: "1.5em", color: "red", display: "flex", alignItems: "center"}}>
        &nbsp; &nbsp; <b>Your turn to bid!</b>
      </div>
    </>
  );

  return (
    <>
    <ScoreGraph scoreGraphVisible={scoreGraphVisible} setScoreGraphVisible={setScoreGraphVisible} {...props} />
    <div style={{display: "flex-inline" }}>
      <div style={{display: "flex" }}>
        <div style={{display: "flex-inline", maxWidth: "150px" }}>
          <Button onClick={showScoreGraph} disabled={loading}>Show Score Graph</Button>
          <Button onClick={toggleAutoPilot} disabled={loading}>{autoPilot ? "Disable" : "Enable"} AutoPilot</Button>
        </div>
        { myTurnToPlay && promptUserToPlay }
        { myTurnToBid && promptUserToBid }
        <TrumpHint trump={trump} leadSuitLetter={leadSuitLetter} />
      </div>
      <hr />
    </div>
    </>
  );
}

export default withRouter(HUD);
