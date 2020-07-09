import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import Card from './Card';

function CardDisplay(props) {
  const {cards} = props;
  const cardComponents = cards.map((card, index) => (
    <Card card={card} key={index} small={false}/>
  ))

  return (
    <div style={{display: "flex"}}>
      {cardComponents}
    </div>
  );
}

export default withRouter(CardDisplay);
