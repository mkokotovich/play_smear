import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Button, Modal } from 'antd';
import axios from 'axios';

import getErrorString from './utils';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


function ScoreGraphVis(props) {
  return (
    <>
      Hi
    </>
  );
}

function ScoreGraph(props) {
  const {scoreGraphVisible, setScoreGraphVisible, game, loading, setLoading, signedInUser} = props;
  const [scoreData, setScoreData] = useState(null);

  React.useEffect(() => {
    if (game) {
      retrieveScoreData();
    }
  }, [game, scoreGraphVisible]);

  function retrieveScoreData() {
    setLoading(true);
    axios.get(`/api/smear/v1/games/${game.id}`).then((response) => {
      setLoading(false);
      setScoreData(response.data);
    }).catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to retrieve score data",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
  }

  function onClose() {
    setScoreGraphVisible(false);
  }

  return (
    <>
      <Modal
        title="Score Graph"
        visible={scoreGraphVisible}
        onCancel={onClose}
        onOk={onClose}
        footer={[
          <Button key="back" onClick={onClose}>
            Close
          </Button>
        ]}
      >
      <ScoreGraphVis scoreData={scoreData} />
      </Modal>
    </>
  );
}

export default withRouter(ScoreGraph);
