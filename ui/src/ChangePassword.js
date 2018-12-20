import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
import './ChangePassword.css';

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

class ChangePassword extends Component {
  state = {
    oldPassword: undefined,
    newPassword: undefined,
    verifyNewPassword: undefined,
    loading: false
  }

  onChangeOldPassword = (e) => {
    this.setState({ oldPassword: e.target.value });
  }

  onChangeNewPassword = (e) => {
    this.setState({ newPassword: e.target.value });
  }

  onChangeVerifyNewPassword = (e) => {
    this.setState({ verifyNewPassword: e.target.value });
  }

  handleCancel = () => {
    this.props.history.goBack();
  }

  handleChange = () => {
    if (!this.state.oldPassword) {
      Modal.error({
        title: "Missing Current Password",
        content: "Please supply your current password",
        maskClosable: true,
      });
      return;
    }
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
    axios.post(`/api/users/v1/changepassword/`,
      {
        old_password: this.state.oldPassword,
        new_password: this.state.newPassword
      }
    )
      .then((response) => {
        console.log(response);
        this.setState({
          loading: false,
        });
        this.props.history.goBack();
      })
      .catch((error) => {
        console.log(error);
        this.setState({loading: false});
        Modal.error({
          title: "Unable to change user's password",
          content: "Unable to change user's password. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    const labelAndInputs = (
      <React.Fragment>
        <ProfileLabelAndInput
          label="Current Password"
          value={this.state.oldPassword}
          onChange={this.onChangeOldPassword}
          password={true}
        />
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
      </React.Fragment>
      );

    return (
      <div className="ChangePassword">
        <h2>Change Password</h2>
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        { labelAndInputs }
        <Row type="flex">
          <Button
            type="default"
            onClick={this.handleCancel}
            className="ChangeButton">
              Cancel
          </Button>
          <Button
            type="primary"
            onClick={this.handleChange}
            className="ChangeButton">
              Update
          </Button>
        </Row>
      </div>
    );
  }
}

export default withRouter(ChangePassword);
