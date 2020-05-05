import React from 'react';

function Card(props) {
  const {card} = props;
  return (
    <div style={{display: "inline-block", padding: 5}}>
      {card} 
    </div>
  );
}

export default Card;
