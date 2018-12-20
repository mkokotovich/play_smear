import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import { Row, Col, Input, Modal, Spin, Button} from 'antd';
import axios from 'axios';
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

class Profile extends Component {
  state = {
    user: undefined,
    loading: false
  }

  componentDidMount(prevProps) {
    if (this.props.user) {
      this.loadUser();
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.user && (!prevProps.user || this.props.user.id !== prevProps.user.id)) {
      this.loadUser();
    }
  }

  loadUser = () => {
    this.setState({loading: true});
    axios.get(`/api/users/v1/${this.props.user.id}/`)
      .then((response) => {
        console.log(response);
        this.setState({
          loading: false,
          user: response.data
        });
      })
      .catch((error) => {
        console.log(error);
        this.setState({loading: false});
        Modal.error({
          title: "Unable to load user profile data",
          content: "Unable to load user profile data. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  onChangeUsername = (e) => {
    var newUser = this.state.user;
    newUser.username = e.target.value;
    this.setState({ user: newUser });
  }

  onChangeFirstName = (e) => {
    var newUser = this.state.user;
    newUser.first_name = e.target.value;
    this.setState({ user: newUser });
  }

  onChangeLastName = (e) => {
    var newUser = this.state.user;
    newUser.last_name = e.target.value;
    this.setState({ user: newUser });
  }

  onChangeEmail = (e) => {
    var newUser = this.state.user;
    newUser.email = e.target.value;
    this.setState({ user: newUser });
  }

  handleCancel = () => {
    this.props.history.goBack();
  }

  handleChangePassword = () => {
    this.props.history.push('/profile/password');
  }

  handleSave = () => {
    this.setState({loading: true});
    axios.patch(`/api/users/v1/${this.props.user.id}/`, this.state.user)
      .then((response) => {
        console.log(response);
        this.setState({
          loading: false,
          user: response.data
        });
        this.props.history.goBack();
      })
      .catch((error) => {
        console.log(error);
        this.setState({loading: false});
        Modal.error({
          title: "Unable to update user profile data",
          content: "Unable to update user profile data. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  render() {
    const labelAndInputs = (this.state.user) ? (
      <React.Fragment>
        <ProfileLabelAndInput label="Username" value={this.state.user.username} onChange={this.onChangeUsername} disabled={true} />
        <ProfileLabelAndInput label="First Name" value={this.state.user.first_name} onChange={this.onChangeFirstName} />
        <ProfileLabelAndInput label="Last Name" value={this.state.user.last_name} onChange={this.onChangeLastName} />
        <ProfileLabelAndInput label="Email" value={this.state.user.email} onChange={this.onChangeEmail} />
        <Button onClick={this.handleChangePassword}>Change Password</Button>
        <br/><br/>
      </React.Fragment>
      ) : '';
    return (
      <div className="Profile">
        <h2>Profile</h2>
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        { labelAndInputs }
        <Row type="flex">
          <Button
            type="default"
            onClick={this.handleCancel}
            className="ProfileButton">
              Cancel
          </Button>
          <Button
            type="primary"
            onClick={this.handleSave}
            className="ProfileButton">
              Update
          </Button>
        </Row>
      </div>
    );
  }
}

export default withRouter(Profile);
