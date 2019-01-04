import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Spin, Input, Popover, Icon, Divider, Button, Row, Col } from 'antd';
import './GameList.css';

class GameList extends Component {
  state = {
  }

  onChangeInput = (e) => {
    this.setState({[e.target.name]: e.target.value});
  }

  render() {
    const { initLoading, gameList, handleDelete, handleJoin, handleResume } = this.props;

    const title = this.props.mode === 'public' ? "Join a game started by someone else" : "Manage My Games";

    const games = gameList.map(game =>
      <div className="GameList" key={game.id}>
        <Row type="flex" align="middle">
          <Col className="GameName" xs={12} md={6}>
            <b>{game.name}</b>
          </Col>
          <Col className="GameIcons" xs={12} md={6}>
            <Popover placement="topLeft" content="The number of players who have joined out of the total number of players this game accepts" title="Players">
              {game.num_joined}/{game.num_players} <Icon type="user" />
            </Popover>
            <span style={{padding: "5px"}}> </span>
            <Popover placement="topLeft" content="The number of teams in this game" title="Teams">
              {game.num_teams} <Icon type="team" />
            </Popover>
            <span style={{padding: "5px"}}> </span>
            <Popover placement="topLeft" content="The number of points needed to win this game" title="Points">
              {game.score_to_play_to} <Icon type="trophy" />
            </Popover>
            <span style={{padding: "5px"}}> </span>
            { game.passcode_required &&
            <Popover placement="topLeft" content="A passcode is required to join this game" title="Passcode Required">
              <Icon type="lock" />
            </Popover>
            }
          </Col>
          <Col xs={24} md={12} align="right">
              {
                !game.loading && this.props.mode === 'manage' ?
                  (
                    <>
                      <Button style={{marginRight: "5px"}} onClick={() => handleResume(game.id)}>Resume</Button>
                      <Button onClick={() => handleDelete(game.id)}>Cancel</Button>
                    </>
                  ) :
                  (
                    <>
                      { game.passcode_required && (
                        <Input
                          className="passcodeInput"
                          placeholder="Passcode required"
                          name={`passcode_${game.id}`}
                          value={this.state[`passcode_${game.id}`]}
                          onChange={this.onChangeInput}
                          onPressEnter={() => handleJoin(game.id, this.state[`passcode_${game.id}`])}
                        />
                      )}
                      <Button onClick={() => handleJoin(game.id, this.state[`passcode_${game.id}`])}>Join</Button>
                    </>
                  )
              }
          </Col>
        </Row>
      </div>
    );

    return (
      <>
        <div align="center">
          { initLoading && <Spin size="large" />}
        </div>
        <h2>{title}</h2>
        {games}
      </>
    );
  }
}

export default withRouter(GameList);
