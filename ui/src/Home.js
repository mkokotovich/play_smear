import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Button,Card, Row, Col, Modal, Spin } from 'antd';
import axios from 'axios';
import CreateGame from './CreateGame';
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
    const multiplayer = !this.props.signedInUser ? (
      <div className="HomeNoAuth">
        <h1>Welcome to Play Smear</h1>
        <Link to="/signin">Sign in or create a free account</Link> to play multiplayer games.
        <br/>
        <br/>
        <Link to="/forgot">Forgot your password?</Link>
      </div>
    ) : (
      <>
        <Link to="/games">Find an existing multiplayer game</Link>
        <p>Or, create a new multiplayer game:</p>
        <CreateGame single={false}/>
        <Button style={{width:300}} >Join An Existing Multiplayer Game</Button>
        <Button style={{width:300}} >Manage Multiplayer Games</Button>
      </>
    );
    const multiplayerTitle = "Play against other people";

    const singleplayer = (
      <>
        <p>Create a single player game:</p>
        <CreateGame single={true}/>
        <Button style={{width:300}} >Manage Single Player Games</Button>
      </>
    );
    const singleplayerTitle = "Play against the computer";

    return (
      <Row type="flex" align="middle" className="Home">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
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
