import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Button, Modal } from 'antd';
import axios from 'axios';

import './WaitingRoom.css';

class WaitingRoom extends Component {

  state = {
  }

  startGame = () => {
    this.props.loading(true);
    axios.post(`/api/smear/v1/games/${this.props.game.id}/start/`)
      .then((response) => {
        this.props.loading(false);
      })
      .catch((error) => {
        console.log(error);
        this.props.loading(false);
        Modal.error({
          title: "Unable to start game",
          content: "Unable to start game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    const playerList = this.props.game.players.map((player, index) => {
      return <div>{player.name}</div>
    });

    return (
      <div className="WaitingRoom">
        Now playing game {this.props.game.name}
        {playerList}
        <Button onClick={this.startGame}>Start Game</Button>
      </div>
    );
  }
}

export default withRouter(WaitingRoom);
