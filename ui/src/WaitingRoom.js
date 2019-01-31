import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { Row, Col, Button, Modal, Icon } from 'antd';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import getErrorString from './utils';

import './WaitingRoom.css';

function removePlayerFromGame(player, gameID, setLoading, removePlayerFromList) {
  setLoading(true);
  axios.delete(`/api/smear/v1/games/${gameID}/player/`,
    { data: { id: player.id } })
    .then((response) => {
      setLoading(false);
      removePlayerFromList(player);
    })
      .catch((error) => {
        console.log(error);
        setLoading(false);
        Modal.error({
          title: "Unable to remove player from game",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });

}

function Player(props) {
  const [loading, setLoading] = useState(false);
  const {player, gameID, removePlayerFromList, removeIsVisible} = props;

  const iconType = loading ? "loading" : "close-circle";

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
        {player.name}
      </Col>
      {removeIsVisible && (
      <Col>
        <Icon theme="twoTone" twoToneColor="#eb2f96" style={{cursor: "pointer", fontSize: '18px'}} disabled={loading} type={iconType} onClick={() => removePlayerFromGame(player, gameID, setLoading, removePlayerFromList)}/>
      </Col>
      )}
      </Row>
    </div>
  );
}

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
          title: "Unable to add computer to game",
          content: getErrorString(error.response.data),
          maskClosable: true,
        })
      });
  
}

function AddComputer(props) {
  const { gameID, addPlayer } = props;
  const [loading, setLoading] = useState(false);

  const icon = loading ? "loading" : "plus";

  return (
    <Button style={{width: "100%"}} disabled={loading} onClick={() => addComputerToGame(gameID, setLoading, addPlayer)}><Icon type={icon} /> Computer Player</Button>
  );
}

function TeamHolder(props) {
  const {players, gameID, removePlayerFromList, removeIsVisible} = props;
  return players.map((item, index) => (
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
            <Player player={item} gameID={gameID} removePlayerFromList={removePlayerFromList} removeIsVisible={removeIsVisible}/>
          </div>
        )}
    </Draggable>
  ))
}

function startGame(teams, gameID, setLoading) {
  const teamList = Object.entries(teams).reduce((accum, item) => {
    const [teamID, teamData] = item;
    const teamInfo = {
      id: teamID,
      players: teamData.list
    }
    accum = [...accum, teamInfo];
    return accum;
  }, []);

  setLoading(true);
  axios.post(`/api/smear/v1/games/${gameID}/start/`, {
    teams: teamList,
  })
    .then((response) => {
      setLoading(false);
    })
    .catch((error) => {
      console.log(error);
      setLoading(false);
      Modal.error({
        title: "Unable to start game",
        content: getErrorString(error.response.data),
        maskClosable: true,
      })
    });
}

function WaitingRoom(props) {
  const [allPlayers, setAllPlayers] = useState([]);
  const [bench, setBench] = useState([]);
  // Build a dict that looks like
  // {
  //   team_id: {
  //     list: <state list>,
  //     setList: <state set list>
  //   }
  // }
  const teams = props.game.teams.reduce((accum, team) => {
    const [list, setList] = useState([]);
    accum[team.id] = {
      list: list,
      setList: setList
    };
    return accum;
  }, {});

  const teamSetters = props.game.teams.reduce((accum, team) => {
    accum[team.id] = teams[team.id].setList;
    return accum;
  }, {});

  const teamLists = props.game.teams.reduce((accum, team) => {
    accum[team.id] = teams[team.id].list;
    return accum;
  }, {});

  const playerListSetters = {
    bench: setBench,
    ...teamSetters
  };

  const playerList = {
    bench: bench,
    ...teamLists
  }

  function removePlayer(list, setList, player) {
    const index = list.indexOf(player)
    if (index !== -1) {
      var listCopy = list.slice();
      listCopy.splice(index, 1);
      setList(listCopy);
    }
    const allIndex = allPlayers.indexOf(player)
    if (allIndex !== -1) {
      var allPlayersCopy = allPlayers.slice();
      allPlayersCopy.splice(allIndex, 1);
      setAllPlayers(allPlayersCopy);
    }
  }

  function addPlayer(player) {
    setBench([...bench, player]);
    setAllPlayers([...allPlayers, player]);
  }

  function resetPlayers() {
    setBench(props.game.players);
    setAllPlayers(props.game.players);
    for (var teamID in teamSetters) {
      teamSetters[teamID]([]);
    }
  }

  function autoAssign() {
    const numTeams = props.game.teams.length;
    const teamIDs = props.game.teams.map((item) => item.id);
    function findSameTeam(teamNum) {
      return props.game.players.filter((item, index) => index % numTeams === teamNum);
    }
    for (var i = 0; i < numTeams; i++) {
      const teamID = teamIDs[i];
      teamSetters[teamID](findSameTeam(i));
    }
    setBench([]);
  }

  useEffect(() => {
    const playersToRemove = allPlayers.filter((player) => {
      return props.game.players.indexOf(player) === -1;
    });
    const playersToAddToBench = props.game.players.filter((player) => {
      return allPlayers.indexOf(player) === -1;
    });
    setAllPlayers(props.game.players);
    var benchWithPlayersRemoved = bench.slice();
    for (var i = 0; i < playersToRemove.length; i++) {
      const playerIndex = benchWithPlayersRemoved.indexOf(playersToRemove[i])
      if (playerIndex !== -1) {
        benchWithPlayersRemoved.splice(playerIndex, 1);
      }
    }
    setBench([...benchWithPlayersRemoved, ...playersToAddToBench]);
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

  const teamDroppables = props.game.teams.map((team, index) => (
    <Col key={index}>
      <Droppable droppableId={""+team.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            style={getListStyle(snapshot.isDraggingOver)}>
              <h4>{team.name}</h4>
              <TeamHolder players={teams[team.id].list} gameID={props.game.id} removePlayerFromList={(player) => removePlayer(teams[team.id].list, teams[team.id].setList, player)} />
              {provided.placeholder}
          </div>
        )}
      </Droppable>
    </Col>
  ));

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
            <TeamHolder players={bench} gameID={props.game.id} removePlayerFromList={(player) => removePlayer(bench, setBench, player)} removeIsVisible={true}/>
            <AddComputer gameID={props.game.id} addPlayer={addPlayer}/>
            {provided.placeholder}
          </div>
      )}
      </Droppable>
      </Col>
        {teamDroppables}
      </Row>
    </DragDropContext>
  );

  return (
    <div className="WaitingRoom">
      Now playing game {props.game.name}
      {dnd}
      <div className="flex">
        <Button onClick={() => startGame(teams, props.game.id, props.loading)}>Start Game</Button>
        { props.game.teams.length > 0 &&
          <>
            <Button onClick={() => autoAssign()}>Auto Assign</Button>
            <Button onClick={() => resetPlayers()}>Reset</Button>
          </>
        }
      </div>
    </div>
  );
}

export default withRouter(WaitingRoom);
