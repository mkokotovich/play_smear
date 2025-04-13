import React from 'react';
// import React, { useState, useEffect } from 'react';
// import Card from './Card';

function TrumpHint(props) {
  const {trump, leadSuitLetter} = props;

  var leadSuit = "";
  var suitPicture = "";
  switch (leadSuitLetter) {
    case "S":
      suitPicture = (<span style={{color: "black", fontSize: "30px"}}>♠️</span>);
      leadSuit = "spades";
      break;
    case "C":
      suitPicture = (<span style={{color: "black", fontSize: "30px"}}>♣️</span>);
      leadSuit = "clubs";
      break;
    case "D":
      suitPicture = (<span style={{color: "red", fontSize: "30px"}}>♦️</span>);
      leadSuit = "diamonds";
      break;
    case "H":
      suitPicture = (<span style={{color: "red", fontSize: "30px"}}>♥️</span>);
      leadSuit = "hearts";
      break;
  }
  const leadSuitMsg = leadSuit ? (<>&nbsp; Lead suit was {leadSuit}: {suitPicture}</>) : "";

  var trumpPicture = "";
  switch (trump) {
    case "spades":
      trumpPicture = (<span style={{color: "black", fontSize: "30px"}}>♠️</span>);
      break;
    case "clubs":
      trumpPicture = (<span style={{color: "black", fontSize: "30px"}}>♣️</span>);
      break;
    case "diamonds":
      trumpPicture = (<span style={{color: "red", fontSize: "30px"}}>♦️</span>);
      break;
    case "hearts":
      trumpPicture = (<span style={{color: "red", fontSize: "30px"}}>♥️</span>);
      break;
  }
  return trump ? (
    <div style={{display: "flex", alignItems: "center"}}>
      &nbsp; &nbsp; Trump is {trump}: {trumpPicture}{leadSuitMsg}
    </div>
  ) : "";
}

export default TrumpHint;
