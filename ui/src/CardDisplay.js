import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Card from './Card';

function CardDisplay(props) {
  const {cards, setCards, cardSelected, clickCard} = props;
  const grid = 6;

  function reorder(list, startIndex, endIndex) {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);

    return result;
  };

  function onDragEnd(result) {
    const { source, destination } = result;

    // dropped outside the list
    if (!destination) {
      return;
    }

    const newCards = reorder(
      cards,
      result.source.index,
      result.destination.index
    );

    setCards(newCards);
  }

  const getItemStyle = (isDragging, draggableStyle) => ({
    // some basic styles to make the items look a bit nicer
    userSelect: 'none',

    // change background color if dragging
    // background: isDragging ? 'lightgreen' : "#E3F0DE",

    // styles we need to apply on draggables
    ...draggableStyle,
  });

  const getListStyle = isDraggingOver => ({
    //background: isDraggingOver ? 'lightblue' : "#E3F0DE",
    display: 'flex',
    padding: grid,
    overflow: 'auto',
  });

  const cardComponents = cards.map((card, index) => (
    <Draggable key={card} draggableId={card} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={getItemStyle(
            snapshot.isDragging,
            provided.draggableProps.style
          )}
        >
          <Card card={card} selected={card === cardSelected} small={false} clickCard={clickCard}/>
        </div>
      )}
    </Draggable>
  ))

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="droppable" direction="horizontal">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            style={getListStyle(snapshot.isDraggingOver)}
            {...provided.droppableProps}
          >
            {cardComponents}
          {provided.placeholder}
        </div>
      )}
    </Droppable>
  </DragDropContext>
  );
}

export default withRouter(CardDisplay);
