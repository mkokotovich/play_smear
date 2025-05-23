import React from 'react';

const moduleStrings = import.meta.glob('./svgcards/*.svg', {
  query: '?react',
  import: "default",
})
const globalCardMap = new Map()
for (const path in moduleStrings) {
  moduleStrings[path]().then((mod) => {
    globalCardMap.set(path, mod);
  })
}

function EmptyComponent() {
  return <></>;
}

function Card(props) {
  const {card, selected, small, clickCard} = props;

  function handleClick(e) {
    e.preventDefault();
    if (clickCard) {
      clickCard(card);
    }
  }

  const cardKey = Array.from(globalCardMap.keys()).find(filename => filename.includes(card));
  const CardComponent = globalCardMap.get(cardKey) || EmptyComponent;
  const cardStyle = small ? {
      height: "auto",
      width: "15vw",
      minWidth: "100px",
      maxWidth: "110px",
  } : {
      height: "auto",
      width: "15vw",
      minWidth: "50px",
      maxWidth: "175px",
  };
  const divStyle = small ? {
    padding: "0px",
  } : {
    padding: "0.3vw",
    border: selected ? "2px solid lightgrey" : "0px",
    borderRadius: "10px",
  };
  return (
    <div style={divStyle} onClick={handleClick}>
      <CardComponent style={cardStyle} />
    </div>
  );
}

export default Card;
