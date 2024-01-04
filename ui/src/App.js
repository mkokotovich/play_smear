import React, { Component } from 'react';
import { Route, Link } from 'react-router-dom';
import { Row, Col } from 'antd';
import TawkMessengerReact from '@tawk.to/tawk-messenger-react';
import './App.css';
import SignIn from './SignIn';
import Login from './Login';
import Home from './Home';
import HowToPlay from './HowToPlay';
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
    if (user && user?.id) {
      window.analytics.identify(user.id, {
        username: user.username,
        is_anonymous: user.is_anonymous,
        first_name: user.first_name,
      });
    };

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
          <Col>
            <SignIn
              handleAuthChange={this.handleAuthChange}
              isSignedIn={this.state.user !== null}
              signedInUser={this.state.user}
            />
          </Col>
        </Row>
        <Route
          exact
          path="/"
          render={() => {
            return <Home handleAuthChange={this.handleAuthChange} signedInUser={this.state.user}/>;
          }}
        />

        <Route
          exact
          path={`/login`}
          render={() => {
            return <Login
              handleAuthChange={this.handleAuthChange}
              isSignedIn={this.state.user !== null}
              signedInUser={this.state.user}
            />;
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
          path={`/manage`}
          render={() => {
            return <GameSelector signedInUser={this.state.user} manage={true} />;
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
        <Route
          exact 
          path={`/rules`}
          render={() => {
            return <HowToPlay/>;
          }}
        />
        <div className="App">
          <TawkMessengerReact
            propertyId="657fc53307843602b803173c"
            widgetId="1hhthkknp"/>
        </div>
      </div>
    );
  }
}

export default App;
