import React, { useEffect} from 'react';
import { Row, Col, Button, Dropdown, Menu } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import decode from 'jwt-decode';
import { signIn, signOut } from './auth_utils';
import { UserOutlined } from '@ant-design/icons';

import SignInForm from './SignInForm'


function SignOut(props) {
  const menuClick = ({ key }) => {
    if (key === "signout") {
      props.handleSignOut();
    } else if (key === "profile") {
      props.handleProfile();
    }
  };

  const menu = (props.user.is_anonymous) ? (
    <Menu onClick={menuClick}>
      <Menu.Item key="signout">Sign Out</Menu.Item>
    </Menu>
  ) : (
    <Menu onClick={menuClick}>
      <Menu.Item key="profile">Profile</Menu.Item>
      <Menu.Item key="signout">Sign Out</Menu.Item>
    </Menu>
  );

  const username = props.user.is_anonymous ? props.user.first_name : props.user.username;

  return (
    <React.Fragment>
      <Dropdown overlay={menu} placement="bottomRight">
        <Button type="default" icon={ <UserOutlined /> }>
          {username}
        </Button>
      </Dropdown>
    </React.Fragment>
  );
}

function signInWithToken(token) {
  localStorage.setItem('id_token', token);
  axios.defaults.headers.common['Authorization'] = "Bearer " + token;
  axios.defaults.xsrfCookieName = "csrftoken";
  axios.defaults.xsrfHeaderName = "X-CSRFToken";
}

function SignIn(props) {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if token exists and isn't expired
    const token = localStorage.getItem('id_token');
    if (token) {
      const decoded = decode(token);
      const current_time = new Date().getTime() / 1000;
      if (decoded.exp && decoded.exp < current_time) {
	/* Token is expired, sign out */
	handleSignOut();
      } else {
	signInWithToken(token);
      }
    }
    const user = localStorage.getItem('user');
    if (user) {
      const user_obj = JSON.parse(user)
      props.handleAuthChange(user_obj);
    }
  }, []);

  const handleSignIn = (email, password) => {
    signIn(email, password, props.handleAuthChange, ()=>{
      console.log("Signed in " + email);
    });
  }

  const handleProfile = () => {
    navigate("/profile");
  }

  const handleSignOut = () => {
    signOut(props.handleAuthChange, ()=>{
      console.log("Signed out");
      navigate("/");
    });
  }

  const signInOrOut = props.isSignedIn ? (
    <SignOut handleSignOut={handleSignOut} handleProfile={handleProfile} user={props.signedInUser} />
  ) : (
    <>
      <SignInForm handleSignIn={handleSignIn} />
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

export default SignIn
