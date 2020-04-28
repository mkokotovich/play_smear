import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Modal, Spin } from 'antd';
import axios from 'axios';
//import queryString from 'query-string';
import WaitingRoom from './WaitingRoom';
import getErrorString from './utils';

import './Game.css';


function loadGame(gameID, setLoading, setGame) {
  setLoading(true);
  axios.get(`/api/smear/v1/games/${gameID}/`)
    .then((response) => {
      console.log(response);
      setLoading(false);
      setGame(response.data);
    })
    .catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to load game",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
}

function reloadGameStatus(gameID, updateGame) {
  axios.get(`/api/smear/v1/games/${gameID}/status/`)
    .then((response) => {
      console.log(response);
      updateGame(response.data);
    })
    .catch((error) => {
      console.log(error);
      Modal.error({
        title: "Unable to reload game status",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
}

const useInterval = (fn: () => void, delay: number) => {
  useEffect(() => {
    const id = setInterval(fn, delay)
    return () => clearInterval(id)
  })
};

function Game(props) {

  const [loading, setLoading] = useState(false);
  const [game, setGame] = useState(null);
  const [needInput, setNeedInput] = useState(true);

  function reloadGame(fullReload, setPolling = undefined) {
    if (setPolling !== undefined) {
      setNeedInput(setPolling);
    }
    if (fullReload) {
      loadGame(props.match.params.gameID, () => {}, setGame);
    } else {
      reloadGameStatus(props.match.params.gameID, updateGame);
    }
  }

  function updateGame(newStatus) {
    setGame({
      ...game,
      ...newStatus
    });
  }

  // Load game if the gameID in the URL ever changes
  useEffect(() => {
    loadGame(props.match.params.gameID, setLoading, setGame);
  }, [props.match.params.gameID])

  // Set a timer to reload game every 2 seconds
  useInterval(() => {
    if (needInput) {
      reloadGameStatus(props.match.params.gameID, updateGame);
    }
  }, 2000);

  var gameDisplay = null;
  if (game) {
    if (game.state  === "starting") {
      gameDisplay = (<WaitingRoom game={game} loading={setLoading} reloadGame={reloadGame}/>);
    } else if (game.state  === '') {
      gameDisplay = (<></>);
    } else {
      gameDisplay = (<></>);
    }
  }

  return (
    <div className="Game">
      <div className="Loading" align="center">
        { loading && <Spin size="large" />}
      </div>
      { gameDisplay }
    </div>
  );
}

export default withRouter(Game);
