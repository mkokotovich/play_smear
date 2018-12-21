import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Modal, Spin, Skeleton, List, Button } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import './GameList.css';

class GameList extends Component {
  state = {
    initLoading: true,
    loading: false,
    gameList: [],
  }

  componentDidMount() {
    this.loadGames();
  }

  componentDidUpdate(prevProps) {
    if (this.props.location.search !== prevProps.location.search) {
      this.setState({gameList: []});
      this.loadGames();
    }
  }

  loadGames = () => {
    this.setState({loading: true});
    const values = queryString.parse(this.props.location.search)
    var query = "";
    var sep = "?";
    if (values.type) {
      query = `${query}${sep}test_type=${values.type}`;
      sep = "&";
    }
    if (values.search) {
      query = `${query}${sep}search=${values.search}`;
      sep = "&";
    }
    if (values.clientid) {
      query = `${query}${sep}client_number=${values.clientid}`;
      sep = "&";
    }
    axios.get(`/api/smear/v1/games/${query}`)
      .then((response) => {
        console.log(response);
        this.setState({
          initLoading: false,
          loading: false,
          gameList: response.data
        });
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
    axios.delete(`/api/smear/v1/games/${gameId}/`)
      .then((response) => {
        console.log(response);
        const games = [...this.state.gameList];
        this.setState({ games: games.filter(item => item.id !== gameId) });
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
    var game_data = {};
    axios.post('/api/smear/v1/games/', game_data)
      .then((response) => {
        console.log(response);
        const gameList = this.state.gameList.concat(response.data)
        this.setState({
          gameList: gameList,
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
    const { initLoading, loading, gameList } = this.state;

    return (
      <>
      <Button onClick={this.handleCreate}>Create New Game</Button>
      <List
        className="GameList"
        loading={initLoading}
        itemLayout="horizontal"
        dataSource={gameList}
        renderItem={item => (
          <List.Item key={item.id} actions={!item.loading && [<a>Join</a>, <a>more</a>]}>
            <Skeleton title={false} loading={item.loading} active>
              <List.Item.Meta
                title={item.name}
                description="Item Description"
              />
              <div>content</div>
            </Skeleton>
          </List.Item>
        )}
      />
      </>
    );
  }
}

export default withRouter(GameList);
