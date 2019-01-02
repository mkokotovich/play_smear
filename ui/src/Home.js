import React, { Component } from 'react';
import { Link, withRouter, Redirect } from 'react-router-dom';
import { Button, Card, Row, Col, Modal, Spin } from 'antd';
import axios from 'axios';
import CreateGame from './CreateGame';
import ActionButton from './ActionButton';
import './Home.css';

class Home extends Component {

  state = {
    loading: false,
    redirectToGames: false,
    redirectToManage: false,
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
    if (this.state.redirectToGames) {
      return <Redirect push to="/games" />
    }
    if (this.state.redirectToManage) {
      return <Redirect push to="/manage" />
    }

    const multiplayer = !this.props.signedInUser ? (
      <div className="HomeNoAuth">
        <Link to="/signin">Sign in or create a free account</Link> to play multiplayer games.
        <br/>
        <br/>
        <Link to="/forgot">Forgot your password?</Link>
      </div>
    ) : (
      <>
        <CreateGame single={false}/>
        <ActionButton buttonText="Join A Game" handleClick={() => this.setState({redirectToGames: true})} />
        <ActionButton buttonText="Manage My Games" handleClick={() => this.setState({redirectToManage: true})} />
      </>
    );
    const multiplayerTitle = "Play against other people";

    const singleplayer = (
      <>
        <CreateGame single={true}/>
        <ActionButton buttonText="Manage My Games" handleClick={() => this.setState({redirectToManage: true})} />
      </>
    );
    const singleplayerTitle = "Play against the computer";

    return (
      <Row type="flex" align="top" className="Home">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <Col xs={24}>
          <h1>Welcome to Play Smear</h1>
        </Col>
        <Col xs={24} md={12} align="center">
          <Card title={singleplayerTitle} style={{ width: 380 }} headStyle={{backgroundColor: "#f0f5f0" }} className="HomeCard">
            {singleplayer}
          </Card>
        </Col>
        <Col xs={24} md={12} align="center">
          <Card title={multiplayerTitle} style={{ width: 380 }} headStyle={{backgroundColor: "#f0f5f0" }} className="HomeCard">
            {multiplayer}
          </Card>
        </Col>
      </Row>
    );
  }
}

export default withRouter(Home);
