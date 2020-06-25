import React from 'react';

const reqSvgs = require.context('./svgcards', true, /\.svg$/)
const paths = reqSvgs.keys()
const cards = paths.map(path => reqSvgs(path))

function Card(props) {
  const {card} = props;
  const cardFile = cards.find(filename => filename.includes(card));
  return (
    <div style={{flex: "1", padding: "5px"}}>
      <img src={cardFile} />
    </div>
  );
}

export default Card;
