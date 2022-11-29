import React from 'react';
// import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
// import Card from './Card';

function TrumpHint(props) {
  const {trump, leadSuitLetter} = props;

  var leadSuit = "";
  switch (leadSuitLetter) {
    case "S":
      leadSuit = ", spades were lead.";
      break;
    case "C":
      leadSuit = ", clubs were lead.";
      break;
    case "D":
      leadSuit = ", diamonds were lead.";
      break;
    case "H":
      leadSuit = ", hearts were lead.";
      break;
  }
  return trump ? (
    <div style={{display: "flex", alignItems: "center"}}>
      &nbsp; &nbsp; Trump is {trump}{leadSuit}
    </div>
  ) : "";
}

export default withRouter(TrumpHint);
