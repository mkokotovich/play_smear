import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import queryString from 'query-string';
import axios from 'axios';
import './ResetPassword.css';

function ProfileLabelAndInput(props) {
  return (
    <Row type="flex" align="middle" className="ProfileLine">
      <Col xs={24} sm={12} md={4}>
        {props.label}
      </Col>
      <Col xs={24} sm={12} md={12} lg={6}>
        <Input
          value={props.value}
          onChange={props.onChange}
          disabled={props.disabled !== undefined ? props.disabled : false}
          type={props.password !== undefined ? "password" : "text"}
        />
      </Col>
    </Row>
  );
}

class ResetPassword extends Component {
  state = {
    newPassword: undefined,
    verifyNewPassword: undefined,
    loading: false
  }

  onChangeNewPassword = (e) => {
    this.setState({ newPassword: e.target.value });
  }

  onChangeVerifyNewPassword = (e) => {
    this.setState({ verifyNewPassword: e.target.value });
  }

  handleCancel = () => {
    this.props.history.push('/');
  }

  handleSubmit = () => {
    if (!this.state.newPassword) {
      Modal.error({
        title: "Missing New Password",
        content: "Please supply your desired new password",
        maskClosable: true,
      });
      return;
    }
    if (this.state.newPassword !== this.state.verifyNewPassword) {
      Modal.error({
        title: "New Passwords Do Not Match",
        content: "New passwords do not match, please type them again",
        maskClosable: true,
      });
      return;
    }

    this.setState({loading: true});

    const values = queryString.parse(this.props.location.search)
    axios.post(`/api/users/v1/resetpassword/`,
      {
        email: values.email,
        token: values.token,
        new_password: this.state.newPassword
      }
    )
      .then((response) => {
        console.log(response);
        this.setState({
          loading: false,
        });
        this.props.history.push('/');
      })
      .catch((error) => {
        console.log(error);
        this.setState({loading: false});
        Modal.error({
          title: "Unable to reset user's password",
          content: "Unable to reset user's password. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    return (
      <div className="ResetPassword">
        <h2>Reset Password</h2>
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <p>Enter your new password below and click submit</p>
        <ProfileLabelAndInput
          label="New Password"
          value={this.state.newPassword}
          onChange={this.onChangeNewPassword}
          password={true}
        />
        <ProfileLabelAndInput
          label="Verify New Password"
          value={this.state.verifyNewPassword}
          onChange={this.onChangeVerifyNewPassword}
          password={true}
        />
        <Row type="flex">
          <Button
            type="default"
            onClick={this.handleCancel}
            className="ResetButton">
              Cancel
          </Button>
          <Button
            type="primary"
            onClick={this.handleSubmit}
            disabled={!this.state.newPassword}
            className="ResetButton">
              Send
          </Button>
        </Row>
      </div>
    );
  }
}

export default withRouter(ResetPassword);
