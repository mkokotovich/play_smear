import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Button, Dropdown, Modal, Space } from 'antd';
import { DownOutlined } from '@ant-design/icons';
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
  const myTurnToPlay = game?.current_trick?.active_player && game?.current_trick?.active_player === myPlayer?.id;
  const myTurnToBid = game?.current_hand?.bidder === myPlayer?.id && game?.state === "bidding";

  React.useEffect(() => {
    const myPlayer = game?.players.find(player => player.user === signedInUser.id);
    const autoPilotEnabled = myPlayer?.is_computer;
    setAutoPilot(autoPilotEnabled);
  }, [game])

  function showScoreGraph() {
    setScoreGraphVisible(true);
  }

  function changeAutoPilot(until_new_hand) {
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/auto_pilot/?until_new_hand=${until_new_hand}`
    ).then((response) => {
      setLoading(false);
      setAutoPilot(!autoPilot);
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

  function handleMenuClick(e) {
    const until_new_hand = e.key === "hand";
    changeAutoPilot(until_new_hand);
  };

  function toggleAutoPilot() {
    changeAutoPilot(false);
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

  const autoPilotMenuItems = [
    {
      label: 'For the rest of the hand',
      key: 'hand',
    },
    {
      label: 'For the rest of the game',
      key: 'forever',
    }
  ];
  const autoPilotMenuProps = {
    items: autoPilotMenuItems,
    onClick: handleMenuClick,
  };
  const autoPilotButton = autoPilot ? (
    <>
      <Button onClick={toggleAutoPilot} disabled={loading}>Disable AutoPlay</Button>
    </>
  ) : (
    <>
      <Dropdown menu={autoPilotMenuProps}>
        <Button>
          Enable AutoPlay
          <DownOutlined />
        </Button>
      </Dropdown>
    </>
  )
  return (
    <>
    <ScoreGraph scoreGraphVisible={scoreGraphVisible} setScoreGraphVisible={setScoreGraphVisible} {...props} />
    <div style={{display: "flex-inline" }}>
      <div style={{display: "flex" }}>
        <div style={{display: "flex-inline", maxWidth: "150px" }}>
          <Button onClick={showScoreGraph} disabled={loading}>Show Score Graph</Button>

          {autoPilotButton}
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
