import React from 'react';

const reqSvgs = require.context('./svgcards', true, /\.svg$/)
const paths = reqSvgs.keys()
const cards = paths.map(path => reqSvgs(path))

function Card(props) {
  const {card, small} = props;
  const cardFile = cards.find(filename => filename.includes(card));
  const cardStyle = small ? {
      height: "auto",
      width: "100px",
  } : {
      height: "auto",
      width: "15vw",
      maxWidth: "150px",
  };
  const divStyle = small ? {
    padding: "0px",
  } : {
    padding: "0.5vw",
  };
  return (
    <div style={divStyle}>
      <img alt={cardFile} style={cardStyle} src={cardFile} />
    </div>
  );
}

export default Card;
