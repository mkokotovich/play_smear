import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Button, Modal, Spin } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import WaitingRoom from './WaitingRoom';

import './Game.css';

class Game extends Component {

  state = {
    loading: false,
    game: null,
  }

  componentDidMount() {
    this.loadGame(this.props.match.params.gameID);
  }

  loading = (isLoading) => {
    this.setState({loading: isLoading});
  }

  loadGame = (gameID) => {
    this.loading(true);
    axios.get(`/api/smear/v1/games/${gameID}/`)
      .then((response) => {
        console.log(response);
        this.loading(false);
        this.setState({
          game: response.data,
        });
      })
      .catch((error) => {
        console.log(error);
        this.loading(false);
        Modal.error({
          title: "Unable to load game",
          content: "Unable to load game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    var gameDisplay = null;
    if (this.state.game) {
      const gameState = this.state.game.status.state;
      if (gameState === 'waiting_for_start') {
        gameDisplay = (<WaitingRoom game={this.state.game} loading={this.loading} />);
      } else if (gameState === '') {
        gameDisplay = (<></>);
      } else {
        gameDisplay = (<></>);
      }
    }
    return (
      <div className="Game">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        { gameDisplay }
      </div>
    );
  }
}

export default withRouter(Game);
