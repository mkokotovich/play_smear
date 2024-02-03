import React, { useState, useContext } from 'react';
import { withRouter } from 'react-router-dom';
import { Radio, Button, Modal } from 'antd';
import axios from 'axios';
import {
  AnimatedAxis, // any of these can be non-animated equivalents
  AnimatedGrid,
  AnimatedLineSeries,
  DataContext,
  XYChart,
} from '@visx/xychart';
import { LegendOrdinal } from "@visx/legend";
import { scaleOrdinal } from '@visx/scale';

import getErrorString from './utils';

const accessors = {
  xAccessor: (d) => d.x,
  yAccessor: (d) => d.y,
};

const range = (start, stop, step) =>
  Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);


function ScoreGraphVis(props) {
  const {scoreData} = props;
  if (!scoreData) {
    return (
      <></>
    );
  }

  const scoreDelta = scoreData.maxScore - scoreData.minScore;
  const numTicks = scoreDelta > 10 ? scoreDelta/2 : scoreDelta;
  const values = range(scoreData.minScore, scoreData.maxScore, 1)

  function getDataForContestant(contestantName) {
    const scores = scoreData.contestantData[contestantName].scores;
    return scores.map((score, index) => ({x: index, y: score}));
  }

  function getColorForContestant(contestantName) {
    return scoreData.contestantData[contestantName].color;
  }

  const ordinalColorScale = scaleOrdinal({
    domain: scoreData.contestants,
    range: scoreData.contestants.map((contestantName, index) => (getColorForContestant(contestantName))),
  });

  const ChartLegend = () => {
    return (
      <LegendOrdinal
        direction="row"
        itemMargin="8px 8px 8px 0"
        scale={ordinalColorScale}
        labelFormat={(label) => label.replace("-", " ")}
        legendLabelProps={{ color: "black" }}
        shape="box"
        style={{
          backgroundColor: "white",
          marginTop: -24,
          paddingLeft: 0,
          color: 'black',
          display: 'flex', // required in addition to `direction` if overriding styles
        }}
      />
    );
  };

  const lineSeries = scoreData && scoreData.contestants.map((contestantName, index) => (
    <AnimatedLineSeries key={index} dataKey={contestantName} colorAccessor={getColorForContestant} data={getDataForContestant(contestantName)} {...accessors} />
  ));

  return (
    <>
      <XYChart height={300} xScale={{ type: 'band' }} yScale={{ type: 'linear' }}>
        <AnimatedAxis label="Score" orientation="left" tickValues={values}/>
        <AnimatedAxis orientation="right" tickValues={values}/>
        <AnimatedGrid columns={false} numTicks={numTicks} />
        {lineSeries}
      </XYChart>
      <ChartLegend />
    </>
  );
}

function ScoreGraph(props) {
  const {scoreGraphVisible, setScoreGraphVisible, game, loading, setLoading, signedInUser} = props;
  const [scoreData, setScoreData] = useState(null);

  React.useEffect(() => {
    if (game && scoreGraphVisible) {
      retrieveScoreData();
    }
  }, [scoreGraphVisible]);

  function retrieveScoreData() {
    setLoading(true);
    axios.get(`/api/smear/v1/games/${game.id}/scores`).then((response) => {
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
