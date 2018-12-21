import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Popover, Icon, Modal, Spin, Skeleton, List, Button } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import './GameList.css';

class GameList extends Component {
  state = {
    initLoading: true,
    loading: false,
    gameList: [],
    width: window.innerWidth,
  }

  componentDidMount() {
    this.loadGames();
    window.addEventListener('resize', this.handleWindowSizeChange);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.handleWindowSizeChange);
  }

  handleWindowSizeChange = () => {
    this.setState({ width: window.innerWidth });
  };

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
    if (this.props.mode === "mine") {
      query = `${query}${sep}owner=${this.props.signedInUser.id}`;
      sep = "&";
    } else if (this.props.mode === "public") {
      query = `${query}${sep}public=true`;
      sep = "&";
    }

    if (values.password_required) {
      query = `${query}${sep}password_required=${values.password_required}`;
      sep = "&";
    }
    if (values.search) {
      query = `${query}${sep}search=${values.search}`;
      sep = "&";
    }
    axios.get(`/api/smear/v1/games/${query}`)
      .then((response) => {
        console.log(response);
        this.setState({
          initLoading: false,
          loading: false,
          gameList: response.data.results
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
        this.setState({ gameList: games.filter(item => item.id !== gameId) });
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

  handleResume = (gameId) => {
    console.log("resume " + gameId);
  }

  handleJoin = (gameId) => {
    console.log("join " + gameId);
  }

  render() {
    const { initLoading, loading, gameList } = this.state;

    const title = this.props.mode === 'mine' ? "My Games" : "Public Games";
    const layout = this.state.width > 600 ? "horizontal" : "vertical";

    return (
      <>
      <Button onClick={this.handleCreate}>Create New Game</Button>
      <br/><br/>
      <h2>{title}</h2>
      <List
        className="GameList"
        bordered={true}
        loading={initLoading}
        itemLayout={layout}
        dataSource={gameList}
        renderItem={item => (
          <List.Item
            key={item.id}
            actions = {!item.loading && this.props.mode === 'mine' ?
              [<Button onClick={() => this.handleResume(item.id)}>Resume</Button>, <Button onClick={() => this.handleDelete(item.id)}>Cancel</Button>] :
              [<Button onClick={() => this.handleJoin(item.id)}>Join</Button>]}>
            <Skeleton title={false} loading={item.loading} active>
              <List.Item.Meta
                description={(<>
                  <b>{item.name}</b>
                  <span style={{padding: "15px"}}> </span>
                  <Popover placement="topLeft" content="The number of players who have joined out of the total number of players this game accepts" title="Players">
                    {item.num_joined}/{item.num_players} <Icon type="user" />
                  </Popover>
                  <span style={{padding: "5px"}}> </span>
                  <Popover placement="topLeft" content="The number of teams in this game" title="Teams">
                    {item.num_teams} <Icon type="team" />
                  </Popover>
                  <span style={{padding: "5px"}}> </span>
                  <Popover placement="topLeft" content="The number of points needed to win this game" title="Points">
                    {item.score_to_play_to} <Icon type="trophy" />
                  </Popover>
                  <span style={{padding: "5px"}}> </span>
                  { item.passcode_required &&
                  <Popover placement="topLeft" content="A passcode is required to join this game" title="Passcode Required">
                    <Icon type="lock" />
                  </Popover>
                  }
                </>)}
              />
            </Skeleton>
          </List.Item>
        )}
      />
      </>
    );
  }
}

export default withRouter(GameList);
