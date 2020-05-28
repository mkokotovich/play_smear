import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Modal, Spin } from 'antd';
import axios from 'axios';
//import queryString from 'query-string';
import WaitingRoom from './WaitingRoom';
import Bidding from './Bidding';
import DeclaringTrump from './DeclaringTrump';
import Trick from './Trick';
import HandResults from './HandResults';
import GameResults from './GameResults';
import Settings from './Settings';
import getErrorString from './utils';

import './Game.css';


function loadGame(gameID, handNum, trickNum, setLoading, setGame) {
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
  const handParam = handNum != 0 && handNum != undefined ? {'hand_num': handNum} : {};
  const trickParam = trickNum != 0 && trickNum != undefined ? {'trick_num': trickNum} : {};
  const queryParams = {
    ...handParam,
    ...trickParam
  };
  setLoading(true);
  axios.get(`/api/smear/v1/games/${gameID}/`, {params: queryParams})
    .then((response) => {
      console.log("loadGame", response);
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

function reloadGameStatus(gameID, handNum, trickNum, setLoading, updateGame) {
  const handParam = handNum != 0 && handNum != undefined ? {'hand_num': handNum} : {};
  const trickParam = trickNum != 0 && trickNum != undefined ? {'trick_num': trickNum} : {};
  const queryParams = {
    ...handParam,
    ...trickParam
  };
  setLoading(true);
  axios.get(`/api/smear/v1/games/${gameID}/status/`, {params: queryParams})
    .then((response) => {
      setLoading(false);
      console.log("reloadGameStatus", response);
      updateGame(response.data);
    })
    .catch((error) => {
      console.log(error);
      setLoading(false);
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
  const {signedInUser} = props;

  function reloadGame(fullReload, setPolling = undefined, displayLoading = false) {
    if (setPolling !== undefined) {
      setNeedInput(setPolling);
    }
    const showLoading = displayLoading ? setLoading : () => {};
    if (fullReload) {
      loadGame(props.match.params.gameID, undefined, undefined, showLoading, setGame);
    } else {
      reloadGameStatus(props.match.params.gameID, game?.current_hand?.num, game?.current_trick?.num, showLoading, updateGame);
    }
  }

  function updateGame(newStatus) {
    var newCurrentHand = newStatus?.current_hand;
    if (!newCurrentHand?.cards) {
      // current_hand update didn't contain cards, and the dict expansion below
      // doesn't work recursively, so cards is lost if we don't grab it from game
      const hand = newStatus.current_hand ? newStatus.current_hand : game.current_hand;
      const cards = game?.current_hand ? game.current_hand.cards : []
      newCurrentHand = {
        ...hand,
        "cards": cards
      }
    }

    setGame({
      ...game,
      ...newStatus,
      "current_hand": newCurrentHand
    });
  }

  // Load game if the gameID in the URL ever changes
  useEffect(() => {
    loadGame(props.match.params.gameID, 0, 0, setLoading, setGame);
  }, [props.match.params.gameID])

  // Set a timer to reload game every 2 seconds
  useInterval(() => {
    if (needInput) {
      reloadGameStatus(props.match.params.gameID, game?.current_hand?.num, game?.current_trick?.num, () => {}, updateGame);
    }
  }, 2000);

  var gameDisplay = null;
  const allProps = {
    game,
    loading,
    setLoading,
    reloadGame,
    signedInUser,
  };
  if (game) {
    if (game.state  === "starting") {
      gameDisplay = (<WaitingRoom {...allProps} />);
    } else if (game.state  === "bidding") {
      gameDisplay = (<Bidding {...allProps} />);
    } else if (game.state  === "declaring_trump") {
      gameDisplay = (<DeclaringTrump {...allProps} />);
    } else if (game.state  === "playing_trick") {
      gameDisplay = (<Trick {...allProps} />);
    } else if (game.state  === "game_over") {
      gameDisplay = (<GameResults {...allProps} />);
    } else {
      gameDisplay = (<>Unknown status {game.state}</>);
    }
  }

  return (
    <div className="Game">
      <div className="Loading" align="center">
        { loading && <Spin size="large" />}
      </div>
      <Settings {...allProps} />
      { gameDisplay }
    </div>
  );
}

export default withRouter(Game);
