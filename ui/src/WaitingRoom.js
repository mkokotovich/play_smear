import React, { Component, useState, useEffect } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Row, Col, Button, Modal, Icon } from 'antd';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

import './WaitingRoom.css';

function removePlayerFromGame(player, gameID, setLoading, removePlayerFromList) {
  setLoading(true);
  axios.delete(`/api/smear/v1/games/${gameID}/player/`,
    { data: { player_id: player.id } })
    .then((response) => {
      setLoading(false);
      removePlayerFromList(player);
    })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to remove player from game",
          content: "Unable to remove player from game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });

}

function Player(props) {
  const [loading, setLoading] = useState(false);

  const iconType = loading ? "loading" : "delete";

  return (
    <div style={{
      width: "200px",
      border: "solid",
      borderWidth: "1px",
      marginBottom: "4px",
      padding: "15px",
    }}>
      <Row type="flex" justify="space-between">
      <Col>
        {props.player.name}
      </Col>
      <Col>
        <Icon style={{cursor: "pointer"}} disabled={loading} type={iconType} onClick={() => removePlayerFromGame(props.player, props.gameID, setLoading, props.removePlayerFromList)}/>
      </Col>
      </Row>
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

function addComputerToGame(gameID, setLoading, addPlayer) {
    setLoading(true);
    axios.post(`/api/smear/v1/games/${gameID}/player/`)
      .then((response) => {
        setLoading(false);
        addPlayer(response.data.meta.computer_player);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to start game",
          content: "Unable to start game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
          maskClosable: true,
        })
      });
  
}

function AddComputer(props) {
  const { gameID, addPlayer } = props;
  const [loading, setLoading] = useState(false);

  const icon = loading ? "loading" : "plus";
  const disable = loading;

  return (
    <Button style={{width: "100%"}} disabled={loading} onClick={() => addComputerToGame(gameID, setLoading, addPlayer)}><Icon type={icon} /> Computer Player</Button>
  );
}

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
            <Player player={item} gameID={props.gameID} removePlayerFromList={props.removePlayerFromList}/>
          </div>
        )}
    </Draggable>
  ))
}

function startGame(teams, gameID, setLoading) {
  setLoading(true);
  axios.post(`/api/smear/v1/games/${gameID}/start/`, {
    teams: teams,
  })
    .then((response) => {
      setLoading(false);
    })
    .catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to start game",
        content: "Unable to start game. Please try again\n\n" + error + "\n\n" + JSON.stringify(error.response.data),
        maskClosable: true,
      })
    });
}


function WaitingRoom(props) {
  const [allPlayers, setAllPlayers] = useState([]);
  const [bench, setBench] = useState([]);
  // TODO: figure out how to do teams, should it be a many-to-many through?
  //var teamLists = [...Array(props.game.numTeams).keys()].map((num) => (
  //));
  const [selected, setSelected] = useState([]);
  const playerListSetters = {
    bench: setBench,
    selected: setSelected
  };
  const playerList = {
    bench: bench,
    selected: selected
  }

  function removePlayer(list, setList, player) {
    const index = list.indexOf(player)
    if (index != -1) {
      var listCopy = list.slice();
      listCopy.splice(index, 1);
      setList(listCopy);
    }
    const allIndex = allPlayers.indexOf(player)
    if (allIndex != -1) {
      var listCopy = allPlayers.slice();
      listCopy.splice(allIndex, 1);
      setAllPlayers(listCopy);
    }
  }

  function addPlayer(player) {
    setBench([...bench, player]);
    setAllPlayers([...allPlayers, player]);
  }

  useEffect(() => {
    const playersToRemove = allPlayers.filter((player) => {
      return props.game.players.indexOf(player) == -1;
    });
    const playersToAddToBench = props.game.players.filter((player) => {
      return allPlayers.indexOf(player) == -1;
    });
    setAllPlayers(props.game.players);
    setBench([...bench, ...playersToAddToBench]);
  }, props.game.players);
  
  function onDragEnd(result) {
    const { source, destination } = result;

    // dropped outside the list
    if (!destination) {
      return;
    }

    if (source.droppableId === destination.droppableId) {
      const items = reorder(
        playerList[source.droppableId],
        source.index,
        destination.index
      );

      playerListSetters[source.droppableId](items);

    } else {
      const result = move(
        playerList[source.droppableId],
        playerList[destination.droppableId],
        source,
        destination
      );

      playerListSetters[source.droppableId](result[source.droppableId]);
      playerListSetters[destination.droppableId](result[destination.droppableId]);
    }
  };

  const dnd = (
    <DragDropContext onDragEnd={onDragEnd}>
      <Row type="flex">
      <Col>
      <Droppable droppableId="bench">
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          style={getListStyle(snapshot.isDraggingOver)}>
            <h4>Players</h4>
            <TeamHolder players={bench} gameID={props.game.id} removePlayerFromList={(player) => removePlayer(bench, setBench, player)}/>
            <AddComputer gameID={props.game.id} addPlayer={addPlayer}/>
            {provided.placeholder}
          </div>
      )}
      </Droppable>
      </Col>
      <Col>
          <Droppable droppableId="selected">
            {(provided, snapshot) => (
              <div
                ref={provided.innerRef}
                style={getListStyle(snapshot.isDraggingOver)}>
                  <h4>Team Name</h4>
                  <TeamHolder players={selected} gameID={props.game.id} removePlayerFromList={(player) => removePlayer(selected, setSelected, player)} />
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
      Now playing game {props.game.name}
      {dnd}
      <Button onClick={() => startGame([], props.game.id, props.loading)}>Start Game</Button>
    </div>
  );
}

export default withRouter(WaitingRoom);
