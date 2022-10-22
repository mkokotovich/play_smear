import React from 'react';
// import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
// import Card from './Card';

function TrumpHint(props) {
  const {trump} = props;

  return trump ? (
    <div style={{display: "flex", alignItems: "center"}}>
      &nbsp; Trump is {trump}
    </div>
  ) : "";
}

export default withRouter(TrumpHint);
