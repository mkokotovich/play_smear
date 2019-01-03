import React, { Component } from 'react';
import { Redirect, withRouter } from 'react-router-dom';
import { Button, Modal, Spin } from 'antd';
import axios from 'axios';
import './CreateGame.css';

class CreateGame extends Component {

  state = {
    loading: false,
    redirectToGame: false,
    gameID: 0,
  }

  handleCreate = () => {
    this.setState({
      loading: true
    });
    var game_data = {
      name: "my game name!",
      num_players: 4,
      num_teams: 4,
      score_to_play_to: 11,
      passcode: "hello",
    };
    axios.post('/api/smear/v1/games/', game_data)
      .then((response) => {
        console.log(response);
        this.setState({
          gameID: response.data.id,
          redirectToGame: true,
          loading: false,
        });
      })
      .catch((error) => {
        console.log(error);
        this.setState({
          loading: false,
        });
        Modal.error({
          title: "Unable to create a new game",
          content: "Unable to create a new game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    if (this.state.redirectToGame) {
      return <Redirect push to={`/games/${this.state.gameID}`} />
    }

    return (
      <div className="CreateGame">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <Button style={{width:300}} onClick={this.handleCreate}>Create New Game</Button>
      </div>
    );
  }
}

export default withRouter(CreateGame);
