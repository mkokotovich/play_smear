import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Row, Modal, Spin } from 'antd';
import axios from 'axios';
import GameList from './GameList';
import './Home.css';

class Home extends Component {

  state = {
    loading: false,
  }

  componentDidMount() {
    this.wakeUpBackend();
  }

  wakeUpBackend = () => {
    this.setState({loading: true});
    axios.get('/up/')
      .then((response) => {
        this.setState({loading: false});
        console.log(response);
      })
      .catch((error) => {
        this.setState({loading: false});
        console.log(error);
        Modal.error({
          title: "Unable to reach server",
          content: "Unable to reach server. Please refresh page and try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    if (!this.props.signedInUser) {
      return (
        <div className="HomeNoAuth">
          <h1>Welcome to Play Smear</h1>
          <div align="center">
            { this.state.loading && <Spin size="large" />}
          </div>
          Sign in to play smear
          <br/>
          <br/>
          <Link to="/forgot">Forgot your password?</Link>
        </div>
      );
    }

    return (
      <div className="Home">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <GameList/>
      </div>
    );
  }
}

export default withRouter(Home);
