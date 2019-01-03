import React from 'react';
import { Row, Col, Modal, Button, Dropdown, Menu } from 'antd';
import { Link, withRouter } from 'react-router-dom';
import axios from 'axios';
import decode from 'jwt-decode';
import { signIn, signOut } from './auth_utils';

import SignInForm from './SignInForm'


function SignOut(props) {
  const menuClick = ({ key }) => {
    if (key === "signout") {
      props.handleSignOut();
    } else if (key === "profile") {
      props.handleProfile();
    }
  };

  const menu = (
    <Menu onClick={menuClick}>
      <Menu.Item key="profile">Profile</Menu.Item>
      <Menu.Item key="signout">Sign Out</Menu.Item>
    </Menu>
  );

  return (
    <React.Fragment>
      <Dropdown overlay={menu} placement="bottomRight">
        <Button type="default" icon="user">
          {props.email}
        </Button>
      </Dropdown>
    </React.Fragment>
  );
}

class SignIn extends React.Component {
  constructor(props) {
    super(props);
    this.handleSignIn = this.handleSignIn.bind(this);
    this.handleSignOut = this.handleSignOut.bind(this);
  }

  componentDidMount() {
    // Check if token exists and isn't expired
    const token = localStorage.getItem('id_token');
    if (token) {
      const decoded = decode(token);
      const current_time = new Date().getTime() / 1000;
      if (decoded.exp && decoded.exp < current_time) {
	/* Token is expired, sign out */
	this.handleSignOut();
      } else {
	this.signInWithToken(token);
      }
    }
    const user = localStorage.getItem('user');
    if (user) {
      const user_obj = JSON.parse(user)
      this.props.handleAuthChange(user_obj);
    }
  }

  signInWithToken(token) {
    localStorage.setItem('id_token', token);
    axios.defaults.headers.common['Authorization'] = "Bearer " + token;
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
  }

  handleSignIn(email, password) {
    signIn(email, password, this.props.handleAuthChange, ()=>{
      console.log("Signed in " + email);
    });
  }

  handleProfile = () => {
    this.props.history.push('/profile');
  }

  handleSignOut = () => {
    signOut(this.props.handleAuthChange, ()=>{
      console.log("Signed out");
      this.props.history.push('/');
    });
  }

  render() {
    const signInOrOut = this.props.isSignedIn ? (
      <SignOut handleSignOut={this.handleSignOut} handleProfile={this.handleProfile} email={this.props.signedInUser.username} />
    ) : (
      <>
        <SignInForm handleSignIn={this.handleSignIn} />
        <Row type="flex" justify="space-between">
          <Col>
            <Link to="/login">Sign up for a free account! </Link>
          </Col>
          <Col>
            <Link to="/forgot">Forgot your password? </Link>
          </Col>
        </Row>
      </>
    );

    return (
      <div className="SignIn">
        {signInOrOut}
      </div>
    );
  }
}

export default withRouter(SignIn)
