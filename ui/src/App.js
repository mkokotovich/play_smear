import axios from 'axios';
import React, { Component, useState, useRef } from 'react';
import { withRouter, Route, Link } from 'react-router-dom';
import { Row, Col } from 'antd';
import TawkMessengerReact from '@tawk.to/tawk-messenger-react';
import './App.css';
import SignIn from './SignIn';
import Login from './Login';
import Home from './Home';
import HowToPlay from './HowToPlay';
import GameSelector from './GameSelector';
import Game from './Game';
import Privacy from './Privacy';
import Profile from './Profile';
import ChangePassword from './ChangePassword';
import ForgotPassword from './ForgotPassword';
import ResetPassword from './ResetPassword';


function App() {

  const tawkMessengerRef = useRef();
  const [user, setUser] = useState(null);

  function setTawkUser(user) {
    axios.get("/api/users/v1/user-hash/").then((response) => {
      const user_hash = response.data.user_hash;
      const name = user.first_name ? `${user.first_name} ${user.last_name || ""}` : user.username;
      tawkMessengerRef.current.setAttributes({
        name: name,
        email: user.username,
        store: user.username,
        hash: user_hash,
      }, function(error) {
        if (error) {
          console.log(`Unable to call setAttributes: ${error}`);
        }
      });
    }).catch((error) => {
      console.log(error);
    });
  }

  function handleAuthChange(user) {
    setUser(user);
    if (user && user?.id) {
      const user_id = user.is_anonymous ? "anonymous" : user.id;
      window.analytics.identify(user_id, {
        username: user.username,
        is_anonymous: user.is_anonymous,
        first_name: user.first_name,
      });
      setTawkUser(user);
    }
  }

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
            handleAuthChange={handleAuthChange}
            isSignedIn={user !== null}
            signedInUser={user}
          />
        </Col>
      </Row>
      <Route
        exact
        path="/"
        render={() => {
          return <Home handleAuthChange={handleAuthChange} signedInUser={user}/>;
        }}
      />

      <Route
        exact
        path={`/login`}
        render={() => {
          return <Login
            handleAuthChange={handleAuthChange}
            isSignedIn={user !== null}
            signedInUser={user}
          />;
        }}
      />
      <Route
        exact
        path={`/games`}
        render={() => {
          return <GameSelector signedInUser={user}/>;
        }}
      />
      <Route
        exact
        path={`/manage`}
        render={() => {
          return <GameSelector signedInUser={user} manage={true} />;
        }}
      />
      <Route
        exact
        path={`/games/:gameID`}
        render={() => {
          return <Game signedInUser={user}/>;
        }}
      />

      <Route
        exact 
        path={`/profile/password`}
        render={() => {
          return <ChangePassword user={user}/>;
        }}
      />
      <Route
        exact 
        path={`/profile`}
        render={() => {
          return <Profile user={user}/>;
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
      <Route
        exact 
        path={`/privacy`}
        render={() => {
          return <Privacy/>;
        }}
      />
      <div className="App">
        <TawkMessengerReact
          propertyId="657fc53307843602b803173c"
          widgetId="1hhthkknp"
          ref={tawkMessengerRef}/>
      </div>
    </div>
  );
}

export default withRouter(App);
