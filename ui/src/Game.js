import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Modal, Spin } from 'antd';
import axios from 'axios';
//import queryString from 'query-string';
import WaitingRoom from './WaitingRoom';
import Bidding from './Bidding';
import DeclaringTrump from './DeclaringTrump';
import getErrorString from './utils';

import './Game.css';


function loadGame(gameID, setLoading, setGame) {
  // {
  // created_at: "2020-04-28T15:57:38.064116Z"
  // current_hand: {id: 4, dealer: 36, bidder: 34, high_bid: 4, cards: ["6C", "4S", "7C", "8H", "JD", "5H"]}
  // deleted_at: null
  // id: 7
  // name: "asdfasdf"
  // num_players: 6
  // num_teams: 2
  // owner: 9
  // passcode_required: false
  // players: [{id: 36, name: "Michelle O", user: 8, team: 18, is_computer: true},…]
  // score_to_play_to: 11
  // single_player: true
  // state: "bidding"
  // teams: [{id: 18, name: "Team 2"}, {id: 17, name: "Team 1"}]
  // updated_at: "2020-04-28T15:57:45.979031Z"
  // }
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

  // TODO allow calls to pass setLoading
  function reloadGame(fullReload, setPolling = undefined, displayLoading = false) {
    if (setPolling !== undefined) {
      setNeedInput(setPolling);
    }
    if (fullReload) {
      const showLoading = displayLoading ? setLoading : () => {};
      loadGame(props.match.params.gameID, showLoading, setGame);
    } else {
      reloadGameStatus(props.match.params.gameID, updateGame);
    }
  }

  function updateGame(newStatus) {
    // current_hand updates don't contain cards, and the dict expansion below
    // doesn't work recursively, so cards is lost if we don't grab it
    const hand = newStatus.current_hand ? newStatus.current_hand : game.current_hand;
    const cards = (game && game.current_hand) ? game.current_hand.cards : []
    const current_hand = {
      ...hand,
      "cards": cards
    }

    setGame({
      ...game,
      ...newStatus,
      "current_hand": current_hand
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
    } else if (game.state  === "bidding") {
      gameDisplay = (<Bidding game={game} loading={loading} setLoading={setLoading} reloadGame={reloadGame} />);
    } else if (game.state  === "declaring_trump") {
      gameDisplay = (<DeclaringTrump game={game} setLoading={setLoading} reloadGame={reloadGame} />);
    } else {
      gameDisplay = (<>Unknown status {game.state}</>);
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
