import React from 'react';

function Bid(props) {
  const {bid} = props;
  const bidMessage = !bid ? "" : bid?.bid === 0 ? "Passed" : `Bid ${bid?.bid}`;
  return (
    <div style={{display: "inline-block", padding: 5}}>
      { bidMessage }
    </div>
  );
}

export default Bid;
