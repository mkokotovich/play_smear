import React, { Component } from 'react';
import { Button } from 'antd';

import './ActionButton.css';

class ActionButton extends Component {

  render() {
    return (
      <div className="ActionButton">
        <Button disabled={this.props.disabled} style={{width:300}} onClick={this.props.handleClick}>{this.props.buttonText}</Button>
      </div>
    );
  }
}

export default ActionButton;
