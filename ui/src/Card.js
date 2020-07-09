import React from 'react';

const reqSvgs = require.context('./svgcards', true, /\.svg$/)
const paths = reqSvgs.keys()
const cards = paths.map(path => reqSvgs(path))

function Card(props) {
  const {card, small} = props;
  const cardFile = cards.find(filename => filename.includes(card));
  const style = small ? {
      height: "auto",
      width: "80px",
  } : {
      height: "auto",
      width: "15vw",
      maxWidth: "150px",
  };
  return (
    <div style={{padding: "0.5vw"}}>
      <img style={style} src={cardFile} />
    </div>
  );
}

export default Card;
