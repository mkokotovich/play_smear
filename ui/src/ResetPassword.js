import React, { useState } from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import queryString from 'query-string';
import axios from 'axios';
import getErrorString from './utils';
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

function ResetPassword(props) {
  const [newPassword, setNewPassword] = useState(undefined);
  const [verifyNewPassword, setVerifyNewPassword] = useState(undefined);
  const [loading, setLoading] = useState(false);

  let navigate = useNavigate();
  let location = useLocation();

  const onChangeNewPassword = (e) => {
    setNewPassword(e.target.value);
  }

  const onChangeVerifyNewPassword = (e) => {
    setVerifyNewPassword(e.target.value);
  }

  const handleCancel = () => {
    navigate("/");
  }

  const handleSubmit = () => {
    if (!newPassword) {
      Modal.error({
        title: "Missing New Password",
        content: "Please supply your desired new password",
        maskClosable: true,
      });
      return;
    }
    if (newPassword !== verifyNewPassword) {
      Modal.error({
        title: "New Passwords Do Not Match",
        content: "New passwords do not match, please type them again",
        maskClosable: true,
      });
      return;
    }

    setLoading(true);

    const values = queryString.parse(location.search);
    axios.post(`/api/users/v1/resetpassword/`,
      {
        email: values.email,
        token: values.token,
        new_password: this.state.newPassword
      }
    )
      .then((response) => {
        setLoading(false);
        navigate("/");
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to reset user's password",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  return (
    <div className="ResetPassword">
      <h2>Reset Password</h2>
      <div align="center">
        { loading && <Spin size="large" />}
      </div>
      <p>Enter your new password below and click submit</p>
      <ProfileLabelAndInput
        label="New Password"
        value={newPassword}
        onChange={onChangeNewPassword}
        password={true}
      />
      <ProfileLabelAndInput
        label="Verify New Password"
        value={verifyNewPassword}
        onChange={onChangeVerifyNewPassword}
        password={true}
      />
      <Row type="flex">
        <Button
          type="default"
          onClick={handleCancel}
          className="ResetButton">
            Cancel
        </Button>
        <Button
          type="primary"
          onClick={handleSubmit}
          disabled={!newPassword}
          className="ResetButton">
            Send
        </Button>
      </Row>
    </div>
  );
}

export default ResetPassword;
