import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Modal, Spin } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import GameList from './GameList';
import './GameSelector.css';
import getErrorString from './utils';

function GameSelector(props) {

  const [mineLoading, setMineLoading] = useState(true);
  const [publicLoading, setPublicLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [myList, setMyList] = useState([]);
  const [publicList, setPublicList] = useState([]);
  const [redirect, setRedirect] = useState(false);
  const [gameID, setGameID] = useState(0);

  let location = useLocation();

  useEffect(() => {
    setPublicList([]);
    loadGames("public");
    if (props.signedInUser) {
      setMyList([]);
      loadGames("mine");
    }
  }, [props.signedInUser, location.search]);

  useEffect(() => {
    setLoading(mineLoading || publicLoading);
  }, [mineLoading, publicLoading]);

  const loadGames = (mode) => {
    setLoading(true);
    const values = queryString.parse(location.search);
    const single = values.single ? values.single : false;
    var query = "";
    if (mode === "mine") {
      query = `?players=${props.signedInUser.id}&single_player=${single}`;
    } else {
      query = "?public=true";

      if (values.password_required) {
        query += `&password_required=${values.password_required}`;
      }
      if (values.search) {
        query += `&search=${values.search}`;
      }
    }
    axios.get(`/api/smear/v1/games/${query}`)
      .then((response) => {
        if (mode === "mine") {
          setMineLoading(false);
          setMyList(response.data.results);
        } else {
          // Separate games that I have joined and games I haven't
          setPublicLoading(false);
          setPublicList(response.data.results);
        }
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to load games",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const handleDelete = (gameId) => {
    console.log("delete " + gameId);
    setLoading(true);
    axios.delete(`/api/smear/v1/games/${gameId}/`)
      .then((response) => {
        console.log(response);
        const games = [...myList];
        setMyList(games.filter(item => item.id !== gameId));
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to delete game",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const handleResume = (gameID) => {
    console.log("resume " + gameID);
    setGameID(gameID);
    setRedirect(true);
  }

  const handleJoin = (gameID, passcode) => {
    console.log("join " + gameID);
    setLoading(true);
    axios.post(`/api/smear/v1/games/${gameID}/join/`, {passcode: passcode})
      .then((response) => {
        setGameID(gameID);
        setLoading(false);
        setRedirect(true);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to join game",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const commonProps = {
    handleDelete: handleDelete,
    handleJoin: handleJoin,
    handleResume: handleResume
  };

  if (redirect) {
    return <Navigate to={`/games/${gameID}`} />
  }

  return (
    <div className="GameSelector">
      <div align="center">
        { loading && <Spin size="large" />}
      </div>
      {props.manage && (
        <>
          <GameList signedInUser={props.signedInUser} mode="manage" gameList={myList} initLoading={mineLoading} {...commonProps} />
          <br/>
        </>
      )}
      {!props.manage && (
        <>
          <GameList mode="public" gameList={publicList} initLoading={publicLoading} {...commonProps} />
          <br/>
        </>
      )}
    </div>
  );
}

export default GameSelector;
