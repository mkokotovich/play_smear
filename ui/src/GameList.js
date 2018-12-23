import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Popover, Icon, Skeleton, List, Button } from 'antd';
import './GameList.css';

class GameList extends Component {
  state = {
    width: window.innerWidth,
  }

  componentDidMount() {
    window.addEventListener('resize', this.handleWindowSizeChange);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.handleWindowSizeChange);
  }

  handleWindowSizeChange = () => {
    this.setState({ width: window.innerWidth });
  };

  render() {
    const { initLoading, gameList, handleDelete, handleJoin, handleResume } = this.props;

    const title = this.props.mode === 'mine' ? "My Games" : "Public Games";
    const layout = this.state.width > 600 ? "horizontal" : "vertical";

    return (
      <>
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
              [<Button onClick={() => handleResume(item.id)}>Resume</Button>, <Button onClick={() => handleDelete(item.id)}>Cancel</Button>] :
              [<Button onClick={() => handleJoin(item.id)}>Join</Button>]}>
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
