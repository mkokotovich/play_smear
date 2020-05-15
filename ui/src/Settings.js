import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Row, Button, Modal } from 'antd';
import axios from 'axios';

import PlayerDisplay from './PlayerDisplay';
import CardDisplay from './CardDisplay';
import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function Settings(props) {
  const [autoPilot, setAutoPilot] = useState(false);
  const {game, loading, setLoading } = props;

  function toggleAutoPilot() {
    setLoading(true);
    axios.post(`/api/smear/v1/games/${game.id}/auto_pilot/`
    ).then((response) => {
      setLoading(false);
      setAutoPilot(!autoPilot);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to change AutoPilot setting",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  return (
    <div>
      <Button onClick={toggleAutoPilot} disabled={loading}>{autoPilot ? "Disable" : "Enable"} AutoPilot</Button>
    </div>
  );
}

export default withRouter(Settings);
