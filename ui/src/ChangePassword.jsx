import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
import getErrorString from './utils';
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

function ChangePassword(props) {
  const [oldPassword, setOldPassword] = useState(undefined);
  const [newPassword, setNewPassword] = useState(undefined);
  const [verifyNewPassword, setVerifyNewPassword] = useState(undefined);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate()

  const onChangeOldPassword = (e) => {
    setOldPassword(e.target.value);
  }

  const onChangeNewPassword = (e) => {
    setNewPassword(e.target.value);
  }

  const onChangeVerifyNewPassword = (e) => {
    setVerifyNewPassword(e.target.value);
  }

  const handleCancel = () => {
    navigate(-1);
  }

  const handleChange = () => {
    if (!oldPassword) {
      Modal.error({
        title: "Missing Current Password",
        content: "Please supply your current password",
        maskClosable: true,
      });
      return;
    }
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
    axios.post(`/api/users/v1/changepassword/`,
      {
        old_password: oldPassword,
        new_password: newPassword
      }
    )
      .then((response) => {
        console.log(response);
        setLoading(false);
        navigate(-1);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to change user's password",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const labelAndInputs = (
    <React.Fragment>
      <ProfileLabelAndInput
        label="Current Password"
        value={oldPassword}
        onChange={onChangeOldPassword}
        password={true}
      />
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
    </React.Fragment>
    );

  return (
    <div className="ChangePassword">
      <h2>Change Password</h2>
      <div align="center">
        { loading && <Spin size="large" />}
      </div>
      { labelAndInputs }
      <Row type="flex">
        <Button
          type="default"
          onClick={handleCancel}
          className="ChangeButton">
            Cancel
        </Button>
        <Button
          type="primary"
          onClick={handleChange}
          className="ChangeButton">
            Update
        </Button>
      </Row>
    </div>
  );
}

export default ChangePassword;
