import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Button, Modal, Spin } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import GameList from './GameList';
import './GameSelector.css';

class GameSelector extends Component {

  state = {
    mineLoading: true,
    publicLoading: true,
    loading: false,
    myList: [],
    publicList: [],
  }

  componentDidMount() {
    if (this.props.signedInUser) {
      this.loadGames("mine");
    }
    this.loadGames("public");
  }

  componentDidUpdate(prevProps) {
    if (this.props.location.search !== prevProps.location.search) {
      this.setState({publicList: []});
      this.loadGames("public");
    }
    if (this.props.signedInUser !== prevProps.signedInUser) {
      this.loadGames("mine");
    }
  }

  loadGames = (mode) => {
    this.setState({loading: true});
    const values = queryString.parse(this.props.location.search)
    var query = "";
    if (mode === "mine") {
      query = `?owner=${this.props.signedInUser.id}`;
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
        console.log(response);
        if (mode === "mine") {
          this.setState({
            mineLoading: false,
            loading: this.state.publicLoading,
            myList: response.data.results
          });
        } else {
          this.setState({
            publicLoading: false,
            loading: this.state.mineLoading,
            publicList: response.data.results
          });
        }
      })
      .catch((error) => {
        console.log(error);
        this.setState({loading: false});
        Modal.error({
          title: "Unable to load games",
          content: "Unable to load games. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  handleDelete = (gameId, mode) => {
    console.log("delete " + gameId);
    axios.delete(`/api/smear/v1/games/${gameId}/`)
      .then((response) => {
        console.log(response);
        if (mode === "mine") {
          const games = [...this.state.myList];
          this.setState({ myList: games.filter(item => item.id !== gameId) });
        } else {
          const games = [...this.state.publicList];
          this.setState({ publicList: games.filter(item => item.id !== gameId) });
        }
      })
      .catch((error) => {
        console.log(error);
        Modal.error({
          title: "Unable to delete game",
          content: "Unable to delete game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
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
        const games = [response.data, ...this.state.myList]
        this.setState({
          myList: games,
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

  handleResume = (gameId) => {
    console.log("resume " + gameId);
  }

  handleJoin = (gameId) => {
    console.log("join " + gameId);
  }

  render() {
    const commonProps = {
      handleDelete: this.handleDelete,
      handleJoin: this.handleJoin,
      handleResume: this.handleResume
    };

    return (
      <div className="GameSelector">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <Button onClick={this.handleCreate}>Create New Game</Button>
        <br/><br/>
        {this.props.signedInUser && (<GameList signedInUser={this.props.signedInUser} mode="mine" gameList={this.state.myList} initLoading={this.mineLoading} {...commonProps} />)}
        <br/>
        <GameList mode="public" gameList={this.state.publicList} initLoading={this.publicLoading} {...commonProps} />
      </div>
    );
  }
}

export default withRouter(GameSelector);
