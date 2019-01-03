import React, { Component } from 'react';
import { Link, withRouter, Redirect } from 'react-router-dom';
import {
  Spin, Form, Input, Tooltip, Icon, Cascader, Select, Row, Col, Checkbox, Button, AutoComplete,
} from 'antd';
import axios from 'axios';
import CreateGame from './CreateGame';
import ActionButton from './ActionButton';
import { signIn, signUp } from './auth_utils';
import './Login.css';

const { Option } = Select;
const AutoCompleteOption = AutoComplete.Option;


class RegistrationForm extends React.Component {
  state = {
    confirmDirty: false,
  };

  handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFieldsAndScroll((err, values) => {
      if (!err) {
        signUp(values.signUpEmail, values.signUpPassword, this.props.handleAuthChange, ()=>{
          this.setState({redirectHome: true});
        })
      }
    });
  }

  handleConfirmBlur = (e) => {
    const value = e.target.value;
    this.setState({ confirmDirty: this.state.confirmDirty || !!value });
  }

  compareToFirstPassword = (rule, value, callback) => {
    const form = this.props.form;
    if (value && value !== form.getFieldValue('signUpPassword')) {
      callback('Passwords do not match');
    } else {
      callback();
    }
  }

  validateToNextPassword = (rule, value, callback) => {
    const form = this.props.form;
    if (value && this.state.confirmDirty) {
      form.validateFields(['confirm'], { force: true });
    }
    callback();
  }

  render() {
    if (this.state.redirectHome) {
      return <Redirect push to="/" />
    }

    const { getFieldDecorator } = this.props.form;

    const prefixSelector = getFieldDecorator('prefix', {
      initialValue: '86',
    })(
      <Select style={{ width: 70 }}>
        <Option value="86">+86</Option>
        <Option value="87">+87</Option>
      </Select>
    );

    return (
      <Form onSubmit={this.handleSubmit} className="login-form">
        <Form.Item>
          {getFieldDecorator('signUpEmail', {
            rules: [{
              type: 'email', message: 'The input is not a valid email address!',
            }, {
              required: true, message: 'Please input your email address!',
            }],
          })(
            <Input prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Email" />
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('signUpPassword', {
            rules: [{
              required: true, message: 'Please input your password!',
            }, {
              validator: this.validateToNextPassword,
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Password"/>
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('confirm', {
            rules: [{
              required: true, message: 'Please confirm your password!',
            }, {
              validator: this.compareToFirstPassword,
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Confirm Password" onBlur={this.handleConfirmBlur} />
          )}
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" className="login-form-button">
            Sign up for free account
          </Button>
        </Form.Item>
      </Form>
    );
  }
}

const WrappedRegistrationForm = Form.create()(RegistrationForm);


class NormalLoginForm extends React.Component {
  state = {};

  handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        signIn(values.email, values.password, this.props.handleAuthChange, ()=>{
          this.setState({redirectHome: true});
        })
      }
    });
  }

  render() {
    if (this.state.redirectHome) {
      return <Redirect push to="/" />
    }
    const { getFieldDecorator } = this.props.form;
    return (
      <Form onSubmit={this.handleSubmit} className="login-form">
        <Form.Item>
          {getFieldDecorator('email', {
            rules: [{ required: true, message: 'Please input your email!' }],
          })(
            <Input prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Email" />
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('password', {
            rules: [{ required: true, message: 'Please input your password!' }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Password" />
          )}
        </Form.Item>
        <Form.Item>
          <Link className="login-form-forgot" to="/forgot">Forgot password</Link>
          <Button type="primary" htmlType="submit" className="login-form-button">
            Log in
          </Button>
        </Form.Item>
      </Form>
    );
  }
}

const WrappedNormalLoginForm = Form.create()(NormalLoginForm);


class Login extends Component {

  state = {
    loading: false,
  }


  render() {
    return (
      <Row type="flex" align="top" className="Login">
        <div align="center">
          { this.state.loading && <Spin size="large" />}
        </div>
        <Col xs={24}>
          <>
            <h2>Sign in, or create a free account to start playing!</h2>
            <br/>
          </>
        </Col>
        <Col xs={24} md={12} align="center">
          <WrappedNormalLoginForm {...this.props} />
        </Col>
        <Col xs={24} md={12} align="center">
          <WrappedRegistrationForm {...this.props} />
        </Col>
      </Row>
    );
  }
}

export default withRouter(Login);
