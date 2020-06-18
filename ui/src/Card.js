import React from 'react';

function Card(props) {
  const {card} = props;
  return (
    <div style={{display: "inline-flex", height: "80px", width: "40px", padding: "5px"}}>
      <p>{card}</p>
    </div>
  );
}

export default Card;
