import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Row, Modal, Spin } from 'antd';
import axios from 'axios';
import GameList from './GameList';
import './GameSelector.css';

class GameSelector extends Component {

  state = {
    loading: false,
  }

  render() {

    return (
      <div className="GameSelector">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        {this.props.signedInUser && (<GameList signedInUser={this.props.signedInUser} mode="mine"/>)}
        <GameList mode="public"/>
      </div>
    );
  }
}

export default withRouter(GameSelector);
