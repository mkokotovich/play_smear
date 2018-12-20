import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
import './ForgotPassword.css';

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

class ForgotPassword extends Component {
  state = {
    email: undefined,
    loading: false,
    sent: false
  }

  onChangeEmail = (e) => {
    this.setState({ email: e.target.value });
  }

  handleCancel = () => {
    this.props.history.push('/');
  }

  handleSend = () => {
    this.setState({loading: true});
    axios.post(`/api/users/v1/generatereset/`,
      {
        email: this.state.email
      }
    )
      .then((response) => {
        console.log(response);
        this.setState({
          loading: false,
          sent: true
        });
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
    if (this.state.sent) {
      return (
        <div className="ForgotPassword">
          <h2>Forgotten Password?</h2>
          <p>Reset email was sent, please check your spam folder and follow the directions to reset your password!</p>
        </div>
      );
    }
    return (
      <div className="ForgotPassword">
        <h2>Forgotten Password?</h2>
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <p>Forgotten password? Fear not! Simply enter your email address below, click Send, then a password reset email will be sent to you. Follow the instructions in the email to reset your password</p>
        <ProfileLabelAndInput
          label="Email Address"
          value={this.state.email}
          onChange={this.onChangeEmail}
        />
        <Row type="flex">
          <Button
            type="default"
            onClick={this.handleCancel}
            className="ForgotButton">
              Cancel
          </Button>
          <Button
            type="primary"
            onClick={this.handleSend}
            disabled={!this.state.email}
            className="ForgotButton">
              Send
          </Button>
        </Row>
      </div>
    );
  }
}

export default withRouter(ForgotPassword);
