import React, { Component, useState } from 'react';
import { Link, withRouter, Redirect } from 'react-router-dom';
import {
} from 'antd';
import { signIn, signUp } from './auth_utils';
import './Login.css';

import {
  Spin,
  Form,
  Input,
  Row,
  Col,
  Button,
} from 'antd';

const formItemLayout = {
  labelCol: {
    xs: {
      span: 24,
    },
    sm: {
      span: 8,
    },
  },
  wrapperCol: {
    xs: {
      span: 24,
    },
    sm: {
      span: 16,
    },
  },
};
const tailFormItemLayout = {
  wrapperCol: {
    xs: {
      span: 24,
      offset: 0,
    },
    sm: {
      span: 16,
      offset: 8,
    },
  },
};

const RegistrationForm = (props) => {
  const [form] = Form.useForm();
  const [redirectHome, setRedirectHome] = useState(false);

  const onFinish = values => {
    console.log('Received values of form: ', values);
    signUp(values.email, values.password, props.handleAuthChange, ()=>{
     setRedirectHome(true);
    })
  };

  if (redirectHome) {
    return <Redirect push to="/" />
  }

  return (
    <Form
      {...formItemLayout}
      form={form}
      name="register"
      onFinish={onFinish}
      initialValues={{
      }}
      scrollToFirstError
      className="login-form"
    >
      <Form.Item
        name="email"
        label="E-mail"
        rules={[
          {
            type: 'email',
            message: 'The input is not valid E-mail!',
          },
          {
            required: true,
            message: 'Please input your E-mail!',
          },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="password"
        label="Password"
        rules={[
          {
            required: true,
            message: 'Please input your password!',
          },
        ]}
        hasFeedback
      >
        <Input.Password />
      </Form.Item>

      <Form.Item
        name="confirm"
        label="Confirm Password"
        dependencies={['password']}
        hasFeedback
        rules={[
          {
            required: true,
            message: 'Please confirm your password!',
          },
          ({ getFieldValue }) => ({
            validator(rule, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
              }

              return Promise.reject('The two passwords that you entered do not match!');
            },
          }),
        ]}
      >
        <Input.Password />
      </Form.Item>

      <Form.Item {...tailFormItemLayout}>
        <Button type="primary" htmlType="submit">
          Register
        </Button>
      </Form.Item>
    </Form>
  );
};


const NormalLoginForm = (props) => {
  const [form] = Form.useForm();
  const [redirectHome, setRedirectHome] = useState(false);

  const onFinish = values => {
    console.log('Received values of form: ', values);
    signIn(values.email, values.password, props.handleAuthChange, ()=>{
      setRedirectHome(true);
    })
  };

  if (redirectHome) {
    return <Redirect push to="/" />
  }

  return (
    <Form
      {...formItemLayout}
      form={form}
      name="login"
      onFinish={onFinish}
      initialValues={{
      }}
      scrollToFirstError
      className="login-form"
    >
      <Form.Item
        name="email"
        label="E-mail"
        rules={[
          {
            type: 'email',
            message: 'The input is not valid E-mail!',
          },
          {
            required: true,
            message: 'Please input your E-mail!',
          },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="password"
        label="Password"
        rules={[
          {
            required: true,
            message: 'Please input your password!',
          },
        ]}
        hasFeedback
      >
        <Input.Password />
      </Form.Item>

      <Form.Item {...tailFormItemLayout}>
        <Link className="login-form-forgot" to="/forgot">Forgot password</Link>
        <Button type="primary" htmlType="submit">
          Sign in
        </Button>
      </Form.Item>
    </Form>
  );
};


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
          <NormalLoginForm {...this.props} />
        </Col>
        <Col xs={24} md={12} align="center">
          <RegistrationForm {...this.props} />
        </Col>
      </Row>
    );
  }
}

export default withRouter(Login);
