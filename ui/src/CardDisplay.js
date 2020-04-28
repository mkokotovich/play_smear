import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';

function Card(props) {
  const {card} = props;
  return (
    <div style={{display: "inline-block", padding: 5}}>
      {card} 
    </div>
  );
}

function CardDisplay(props) {
  const {cards} = props;
  const cardComponents = cards.map((card, index) => (
    <Card card={card} key={index} />
  ))

  return (
    <div>
      {cardComponents}
    </div>
  );
}

export default withRouter(CardDisplay);
