import React, { Component } from 'react';
import { Route, Link } from 'react-router-dom';
import { Row, Col } from 'antd';
import './App.css';
import SignIn from './SignIn';
import Home from './Home';
import GameSelector from './GameSelector';
import Game from './Game';
import Profile from './Profile';
import ChangePassword from './ChangePassword';
import ForgotPassword from './ForgotPassword';
import ResetPassword from './ResetPassword';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      user: null,
      assessmentBySlug: {},
    };
  }

  setAssessmentBySlug = (abs) => {
    this.setState({assessmentBySlug: abs});
  }

  componentDidMount() {
  }

  handleAuthChange = (user) => {
    this.setState({
      user: user,
    });
  }

  render() {
    return (
      <div className="App">
        <Row
          type="flex"
          justify="space-between"
          className="navbar"
          align="middle"
          >
          <Col className="Logo"><Link to="/">Play Smear</Link></Col>
          <Col><SignIn handleAuthChange={this.handleAuthChange} /></Col>
        </Row>
        <Route
          exact
          path="/"
          render={() => {
            return <Home signedInUser={this.state.user}/>;
          }}
        />

        <Route
          exact
          path={`/games`}
          render={() => {
            return <GameSelector signedInUser={this.state.user}/>;
          }}
        />
        <Route
          exact
          path={`/games/:gameID`}
          render={() => {
            return <Game signedInUser={this.state.user}/>;
          }}
        />

        <Route
          exact 
          path={`/profile/password`}
          render={() => {
            return <ChangePassword user={this.state.user}/>;
          }}
        />
        <Route
          exact 
          path={`/profile`}
          render={() => {
            return <Profile user={this.state.user}/>;
          }}
        />
        <Route
          exact 
          path={`/reset`}
          render={() => {
            return <ResetPassword/>;
          }}
        />
        <Route
          exact 
          path={`/forgot`}
          render={() => {
            return <ForgotPassword/>;
          }}
        />
      </div>
    );
  }
}

export default App;
