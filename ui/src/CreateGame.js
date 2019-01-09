import React, { Component } from 'react';
import { Redirect, withRouter } from 'react-router-dom';
import { Radio, Row, Checkbox, Input, Button, Modal, Spin } from 'antd';
import axios from 'axios';
import './CreateGame.css';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;

class CreateGame extends Component {

  state = {
    loading: false,
    redirectToGame: false,
    gameID: 0,
    visible: false,
    gameName: "",
    passcode: "",
    requirePasscode: false,
    numPlayers: null,
    numTeams: null,
    scoreToPlayTo: null,
  }

  handleCreate = () => {
    if (!this.readyToStart()) {
      return;
    }
    this.setState({
      loading: true
    });
    var game_data = {
      name: this.state.gameName,
      passcode: this.state.passcode,
      num_players: this.state.numPlayers,
      num_teams: this.state.numTeams ? this.state.numTeams : 0,
      score_to_play_to: this.state.scoreToPlayTo,
      single_player: this.props.single,
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

  onChangeInput = (e) => {
    this.setState({[e.target.name]: e.target.value});
  }

  onChangeCheck = (e) => {
    this.setState({[e.target.name]: e.target.checked});
  }

  onCancel = () => {
    this.setState({
      visible: false,
      gameName: "",
      passcode: "",
      requirePasscode: false,
      numPlayers: null,
      numTeams: null,
      scoreToPlayTo: null,
    });
  }


  readyToStart = () => {
    return (
      (this.state.gameName.length > 0) &&
      (this.state.requirePasscode === false || (this.state.requirePasscode === true && this.state.passcode.length > 0)) &&
      (this.state.scoreToPlayTo && this.state.scoreToPlayTo > 0) &&
      (this.state.numPlayers && this.state.numPlayers > 0)
    );
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
        <Modal
          title={`Start a ${this.props.single ? "single player" : "multiplayer"} game`}
          visible={this.state.visible}
          onOk={this.handleCreate}
          okText="Create Game"
          okButtonProps={{ disabled: !this.readyToStart()}}
          onCancel={this.onCancel}
        >
          <Row className="create_div">
            <Input
              className="create_input"
              placeholder="Game Name"
              name="gameName"
              value={this.state.gameName}
              onChange={this.onChangeInput}
              onPressEnter={() => this.handleCreate()}
            />
          </Row>
          <Row className="create_div">
            <p className="inputLabel">Number of players:</p>
            <RadioGroup name="numPlayers" onChange={this.onChangeInput}>
              <RadioButton value="2">2</RadioButton>
              <RadioButton value="3">3</RadioButton>
              <RadioButton value="4">4</RadioButton>
              <RadioButton value="5">5</RadioButton>
              <RadioButton value="6">6</RadioButton>
              <RadioButton value="7">7</RadioButton>
              <RadioButton value="8">8</RadioButton>
            </RadioGroup>
          </Row>
          <Row className="create_div">
            <p className="inputLabel">Number of teams:</p>
            <RadioGroup name="numTeams" onChange={this.onChangeInput}>
              <RadioButton value="0">No teams</RadioButton>
              <RadioButton value="2">2</RadioButton>
              <RadioButton value="3">3</RadioButton>
              <RadioButton value="4">4</RadioButton>
            </RadioGroup>
          </Row>
          <Row className="create_div">
            <p className="inputLabel">Score to play to:</p>
            <RadioGroup name="scoreToPlayTo" onChange={this.onChangeInput}>
              <RadioButton value="11">11</RadioButton>
              <RadioButton value="15">15</RadioButton>
              <RadioButton value="21">21</RadioButton>
            </RadioGroup>
          </Row>
          { !this.props.single &&
          <Row type="flex" className="create_div">
            <Checkbox
              value={this.state.requirePasscode}
              name="requirePasscode"
              onChange={this.onChangeCheck}
            >
              Require passcode to join
            </Checkbox>
            <Input
              className="create_input"
              placeholder="Passcode"
              name="passcode"
              value={this.state.passcode}
              disabled={!this.state.requirePasscode}
              onChange={this.onChangeInput}
              onPressEnter={() => this.handleCreate()}
            />
          </Row>
          }
        </Modal>
        <Row>
          <Button style={{width:300}} onClick={() => this.setState({visible: true})}>Create New Game</Button>
        </Row>
      </div>
    );
  }
}

export default withRouter(CreateGame);
