import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Button, Modal, Spin } from 'antd';
import axios from 'axios';
import queryString from 'query-string';
import './Game.css';

class Game extends Component {

  state = {
    loading: false,
  }

  render() {
    return (
      <div className="Game">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        Now playing game {this.props.match.params.gameID}
      </div>
    );
  }
}

export default withRouter(Game);
