import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
import getErrorString from './utils';
import './Profile.css';

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
        />
      </Col>
    </Row>
  );
}

function Profile(props) {
  const [user, setUser] = useState(undefined);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadUser();
  }, [props.user]);

  const loadUser = () => {
    setLoading(true);
    axios.get(`/api/users/v1/${props.user.id}/`)
      .then((response) => {
        console.log(response);
        setLoading(false);
        setUser(response.data);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to load user profile data",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const onChangeFirstName = (e) => {
    var newUser = user;
    newUser.first_name = e.target.value;
    setUser(newUser);
  }

  const onChangeLastName = (e) => {
    var newUser = user;
    newUser.last_name = e.target.value;
    setUser(newUser);
  }

  // email is stored in username
  const onChangeEmail = (e) => {
    var newUser = user;
    newUser.username = e.target.value;
    setUser(newUser);
  }

  const handleCancel = () => {
    navigate(-1)
  }

  const handleChangePassword = () => {
    navigate("/profile/password");
  }

  const handleSave = () => {
    setLoading(true);
    axios.patch(`/api/users/v1/${props.user.id}/`, user)
      .then((response) => {
        setLoading(false);
        setUser(response.data);
        navigate(-1)
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to update user profile data",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  }

  const labelAndInputs = (user) ? (
    <React.Fragment>
      <ProfileLabelAndInput label="Email" value={user.username} onChange={onChangeEmail} disabled={true} />
      <ProfileLabelAndInput label="First Name" value={user.first_name} onChange={onChangeFirstName} />
      <ProfileLabelAndInput label="Last Name" value={user.last_name} onChange={onChangeLastName} />
      <Button onClick={handleChangePassword}>Change Password</Button>
      <br/><br/>
    </React.Fragment>
    ) : '';

  return (
    <div className="Profile">
      <h2>Profile</h2>
      <div align="center">
        { loading && <Spin size="large" />}
      </div>
      { labelAndInputs }
      <Row type="flex">
        <Button
          type="default"
          onClick={handleCancel}
          className="ProfileButton">
            Cancel
        </Button>
        <Button
          type="primary"
          onClick={handleSave}
          className="ProfileButton">
            Update
        </Button>
      </Row>
    </div>
  );
}

export default Profile;
