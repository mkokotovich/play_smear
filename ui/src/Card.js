import React from 'react';

const reqSvgs = require.context('./svgcards', true, /\.svg$/)
const paths = reqSvgs.keys()
const cards = paths.map(path => reqSvgs(path))

function Card(props) {
  const {card, selected, small, clickCard} = props;

  function handleClick(e) {
    e.preventDefault();
    if (clickCard) {
      clickCard(card);
    }
  }

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
    border: selected ? "2px solid lightgrey" : "0px",
    borderRadius: "10px",
  };
  return (
    <div style={divStyle} onClick={handleClick}>
      <img alt={cardFile} style={cardStyle} src={cardFile} />
    </div>
  );
}

export default Card;
