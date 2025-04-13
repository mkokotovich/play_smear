import axios from 'axios';
import getErrorString from './utils';
import { Modal } from 'antd';


export function signIn(email, password, handleAuthChange, successCallback) {
  console.log("Trying to sign in " + email);
  axios.post('/api/auth/', {
    username: email,
    password: password
  })
  .then((response) => {
    const token = response.data.token;
    const user = response.data.user;
    console.log(response.headers);
    if (token) {
      console.log("Signed in " + email);
      localStorage.setItem('id_token', token);
      axios.defaults.headers.common['Authorization'] = "Bearer " + token;
      axios.defaults.xsrfCookieName = "csrftoken";
      axios.defaults.xsrfHeaderName = "X-CSRFToken";
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
        if (handleAuthChange) {
          console.log("Calling handleAuthChange with user" + JSON.stringify(user));
          handleAuthChange(user);
        }
      }
      if (successCallback) {
        successCallback();
      }
    } else {
      console.log("Failed to sign in " + email);
      Modal.error({
        title: "Unable to sign in",
        content: "Please check email and password and try again",
        maskClosable: true,
      })
    }
  })
  .catch((error) => {
    console.log(error);
    Modal.error({
      title: "Unable to sign in",
      content: "Please check email and password and try again",
      maskClosable: true,
    })
  });
}

export function signUp(email, password, handleAuthChange, successCallback) {
  console.log("Trying to sign up " + email);
  axios.post('/api/users/v1/', {
    username: email,
    password: password
  })
  .then((response) => {
    console.log("Signed " + email + " up for an account");
    return signIn(email, password, handleAuthChange, successCallback);
  })
  .catch((error) => {
    console.log(error);
    Modal.error({
      title: "Unable to sign up",
      content: getErrorString(error.response.data),
      maskClosable: true,
    })
  });
}

export function signOut(handleAuthChange, successCallback) {
  localStorage.removeItem("id_token");
  localStorage.removeItem("user");
  if (handleAuthChange) {
    handleAuthChange(null);
  }
  delete axios.defaults.headers.common["Authorization"];

  console.log("Signed out");
  if (successCallback) {
    successCallback();
  }
}
