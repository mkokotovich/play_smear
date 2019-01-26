import React, { Component, useEffect } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Row, Col, Button, Modal } from 'antd';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

import './WaitingRoom.css';

function Player(props) {
  return (
    <div style={{
      width: "200px",
      border: "solid",
      borderWidth: "1px",
      marginBottom: "4px",
      padding: "15px",
    }}>
      {props.player.name}
    </div>
  );
}


// fake data generator
const getItems = (count, offset = 0) =>
    Array.from({ length: count }, (v, k) => k).map(k => ({
        id: `item-${k + offset}`,
        content: `item ${k + offset}`
    }));

// a little function to help us with reordering the result
const reorder = (list, startIndex, endIndex) => {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);

    return result;
};

/**
 * Moves an item from one list to another list.
 */
const move = (source, destination, droppableSource, droppableDestination) => {
    const sourceClone = Array.from(source);
    const destClone = Array.from(destination);
    const [removed] = sourceClone.splice(droppableSource.index, 1);

    destClone.splice(droppableDestination.index, 0, removed);

    const result = {};
    result[droppableSource.droppableId] = sourceClone;
    result[droppableDestination.droppableId] = destClone;

    return result;
};

const getItemStyle = (isDragging, draggableStyle) => ({
    // some basic styles to make the items look a bit nicer
    userSelect: 'none',

    // change background colour if dragging
    background: isDragging ? 'lightgreen' : 'white',

    // styles we need to apply on draggables
    ...draggableStyle
});

const getListStyle = isDraggingOver => ({
    background: isDraggingOver ? 'lightblue' : 'lightgrey',
    margin: 5,
    padding: 5,
    minWidth: 210,
    minHeight: 200
});

function TeamHolder(props) {
  return props.players.map((item, index) => (
    <Draggable
      key={item.id}
      draggableId={item.id}
      index={index}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            style={getItemStyle(
              snapshot.isDragging,
              provided.draggableProps.style
            )}>
            <Player player={item} />
          </div>
        )}
    </Draggable>
  ))
}


class WaitingRoom extends Component {
  componentDidMount = () => {
    this.setState({humans: this.props.game.players});
  }

  state = {
    humans: [],
    computers: [],
    selected: []
  }

  startGame = () => {
    this.props.loading(true);
    axios.post(`/api/smear/v1/games/${this.props.game.id}/start/`, {
      teams: [],
    })
      .then((response) => {
        this.props.loading(false);
      })
      .catch((error) => {
        console.log(error);
        this.props.loading(false);
        Modal.error({
          title: "Unable to start game",
          content: "Unable to start game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  }

  getList = id => this.state[id];

  onDragEnd = result => {
    const { source, destination } = result;

    // dropped outside the list
    if (!destination) {
      return;
    }

    if (source.droppableId === destination.droppableId) {
      const items = reorder(
        this.getList(source.droppableId),
        source.index,
        destination.index
      );

      this.setState({[source.droppableId]: items });

    } else {
      const result = move(
        this.getList(source.droppableId),
        this.getList(destination.droppableId),
        source,
        destination
      );

      this.setState({
        [source.droppableId]: result[source.droppableId],
        [destination.droppableId]: result[destination.droppableId]
      });
    }
  };


  render() {
    let dnd = (
      <DragDropContext onDragEnd={this.onDragEnd}>
        <Row type="flex">
        <Col>
        <Droppable droppableId="humans">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            style={getListStyle(snapshot.isDraggingOver)}>
              <h4>Human Players</h4>
              <TeamHolder players={this.state.humans} />
              {provided.placeholder}
            </div>
        )}
        </Droppable>
        <Droppable droppableId="computers">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            style={getListStyle(snapshot.isDraggingOver)}>
              <h4>Computer Players</h4>
              <TeamHolder players={this.state.computers} />
              {provided.placeholder}
            </div>
        )}
        </Droppable>
        </Col>
        <Col style={{minHeight: "400px"}}>
            <Droppable droppableId="selected" style={{minHeight: "400px"}}>
              {(provided, snapshot) => (
                <div
                ref={provided.innerRef}
                  style={getListStyle(snapshot.isDraggingOver)}>
                    <h4>Team Name</h4>
                    <TeamHolder players={this.state.selected} />
                    {provided.placeholder}
                    </div>
              )}
            </Droppable>
        </Col>
        </Row>
      </DragDropContext>
    );

    return (
      <div className="WaitingRoom">
        Now playing game {this.props.game.name}
        {dnd}
        <Button onClick={this.startGame}>Start Game</Button>
      </div>
    );
  }
}

export default withRouter(WaitingRoom);
