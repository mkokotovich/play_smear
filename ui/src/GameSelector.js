import React, { Component } from 'react';
import { Redirect, withRouter } from 'react-router-dom';
import { Modal, Spin } from 'antd';
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
    redirect: false,
    gameID: 0,
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
          // Separate games that I have joined and games I haven't
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

  handleDelete = (gameId) => {
    console.log("delete " + gameId);
    this.setState({
      loading: true
    });
    axios.delete(`/api/smear/v1/games/${gameId}/`)
      .then((response) => {
        console.log(response);
        const games = [...this.state.myList];
        this.setState({
          myList: games.filter(item => item.id !== gameId),
          loading: false,
        });
      })
      .catch((error) => {
        console.log(error);
        this.setState({
          loading: false,
        });
        Modal.error({
          title: "Unable to delete game",
          content: "Unable to delete game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  handleResume = (gameID) => {
    console.log("resume " + gameID);
    this.setState({
      redirect: true,
      gameID: gameID,
    });
  }

  handleJoin = (gameID) => {
    console.log("join " + gameID);
    this.setState({
      loading: true
    });
    axios.post(`/api/smear/v1/games/${gameID}/join/`)
      .then((response) => {
        this.setState({
          redirect: true,
          gameID: gameID,
          loading: false,
        });
      })
      .catch((error) => {
        console.log(error);
        this.setState({
          loading: false,
        });
        Modal.error({
          title: "Unable to join game",
          content: "Unable to join game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    const commonProps = {
      handleDelete: this.handleDelete,
      handleJoin: this.handleJoin,
      handleResume: this.handleResume
    };

    if (this.state.redirect) {
      return <Redirect push to={`/games/${this.state.gameID}`} />
    }

    return (
      <div className="GameSelector">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        {this.props.manage && (
          <>
            <GameList signedInUser={this.props.signedInUser} mode="manage" gameList={this.state.myList} initLoading={this.mineLoading} {...commonProps} />
            <br/>
          </>
        )}
        {!this.props.manage && (
          <>
            <GameList mode="public" gameList={this.state.publicList} initLoading={this.publicLoading} {...commonProps} />
            <br/>
          </>
        )}
      </div>
    );
  }
}

export default withRouter(GameSelector);
