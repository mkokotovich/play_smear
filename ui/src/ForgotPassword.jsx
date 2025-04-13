import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
import getErrorString from './utils';
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

function ForgotPassword(props) {
  const [email, setEmail] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const navigate = useNavigate();

  const onChangeEmail = (e) => {
    setEmail(e.target.value);
  }

  const handleCancel = () => {
    navigate(-1);
  }

  const handleSend = () => {
    setLoading(true);
    axios.post(`/api/users/v1/generatereset/`,
      {
        email: email
      }
    )
      .then((response) => {
        console.log(response);
        setLoading(false);
        setSent(true);
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

  if (sent) {
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
        { loading && <Spin size="large" />}
      </div>
      <p>Forgotten password? Fear not! Simply enter your email address below, click Send, then a password reset email will be sent to you. Follow the instructions in the email to reset your password</p>
      <ProfileLabelAndInput
        label="Email Address"
        value={email}
        onChange={onChangeEmail}
      />
      <Row type="flex">
        <Button
          type="default"
          onClick={handleCancel}
          className="ForgotButton">
            Cancel
        </Button>
        <Button
          type="primary"
          onClick={handleSend}
          disabled={!email}
          className="ForgotButton">
            Send
        </Button>
      </Row>
    </div>
  );
}

export default ForgotPassword;
