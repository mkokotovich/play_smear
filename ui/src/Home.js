import React, { Component } from 'react';
import { Link, withRouter, Redirect } from 'react-router-dom';
import { Card, Row, Col, Modal, Spin } from 'antd';
import axios from 'axios';
import CreateGame from './CreateGame';
import ActionButton from './ActionButton';
import getErrorString from './utils';
import './Home.css';

class Home extends Component {

  state = {
    loading: false,
    redirectToGames: false,
    redirectToManage: false,
    redirectToHowToPlay: false,
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
          content: "Please refresh page and try again. " + getErrorString(error.response?.data),
          maskClosable: true,
        })
      });
  }

  render() {
    if (this.state.redirectToGames) {
      return <Redirect push to="/games" />
    }
    if (this.state.redirectToManage) {
      return <Redirect push to={`/manage?single=${this.state.single}`} />
    }
    if (this.state.redirectToHowToPlay) {
      return <Redirect push to={`/rules`} />
    }

    const signedIn = this.props.signedInUser && !this.props.signedInUser.is_anonymous;

    const multiplayer = !signedIn ? (
      <div className="HomeNoAuth">
        <Link to="/login">Sign in or create a free account</Link> to play multiplayer games.
      </div>
    ) : (
      <>
        <CreateGame single={false}/>
        <ActionButton buttonText="Join A Game" handleClick={() => this.setState({redirectToGames: true})} />
        <ActionButton buttonText="Resume A Game" handleClick={() => this.setState({
          redirectToManage: true,
          single: false,
        })} />
      </>
    );
    const multiplayerTitle = "Play against other people";

    const singleplayer = (
      <>
        <CreateGame single={true} handleAuthChange={this.props.handleAuthChange} />
        <ActionButton disabled={!signedIn} buttonText="Resume A Game" handleClick={() => this.setState({
          redirectToManage: true,
          single: true,
        })} />
      </>
    );
    const singleplayerTitle = "Play against the computer";
    const howToPlayTitle = "How to play";
    const howToPlay = (
      <>
        <ActionButton buttonText="View Rules" handleClick={() => this.setState({
          redirectToHowToPlay: true,
        })} />
      </>
    );

    return (
      <Row type="flex" align="top" className="Home">
        <div className="Loading" align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <Col xs={24}>
          <div style={{maxWidth: 1200, padding: "0px 20px 0px 20px"}} >
            <h1>Welcome to Play Smear!</h1>
            <p>Welcome to the new Play Smear, now featuring the ability to resume games, more easily discover multiplayer games, and an overall improved user experience!</p>
            <p>To take advantage of all the new features, please <Link to="/login">create a free account</Link>. Otherwise, single player games against the computer can still be played without logging in.</p>
          </div>
        </Col>
        <Col xs={24} md={12} lg={8} align="center">
          <Card title={singleplayerTitle} style={{ width: 340 }} headStyle={{backgroundColor: "#f0f5f0" }} className="HomeCard">
            {singleplayer}
          </Card>
        </Col>
        <Col xs={24} md={12} lg={8} align="center">
          <Card title={multiplayerTitle} style={{ width: 340 }} headStyle={{backgroundColor: "#f0f5f0" }} className="HomeCard">
            {multiplayer}
          </Card>
        </Col>
        <Col xs={24} md={12} lg={8} align="center">
          <Card title={howToPlayTitle} style={{ width: 340 }} headStyle={{backgroundColor: "#f0f5f0" }} className="HomeCard">
            {howToPlay}
          </Card>
        </Col>
      </Row>
    );
  }
}

export default withRouter(Home);
