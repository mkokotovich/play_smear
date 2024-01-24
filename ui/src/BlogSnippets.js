import React, { useState, useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Card from './Card';
import axios from 'axios';

function BlogSnippets(props) {
  const [posts, setPosts] = useState([]);

  function retrievePosts() {
    axios.get("/api/blog-proxy").then((response) => {
      const newPosts = response.data.feed.entry.map((entry, index) => {
        return {
          title: entry.title["$t"],
          content: entry.summary["$t"],
          link: entry.link.filter((link) => link.rel === "alternate")[0].href,
        };
      });
      setPosts(newPosts);
    }).catch((error) => {
      console.log(error);
    });
  }

  useEffect(() => {
    retrievePosts();
  }, []);
  
  const postsDisplayed = posts.map((post, index) => (
    <div key={index} align="left" style={{fontSize: "12px"}}>
      <hr/>
      <h4><a href={post.link} target="_blank" rel="noopener noreferrer">{post.title}</a></h4>
      <span dangerouslySetInnerHTML={{__html: post.content}}></span>
    </div>
  ));

  return (
    <div style={{maxHeight: "200px", "overflowY": "scroll"}}>
      {postsDisplayed}
    </div>
  );
}

export default withRouter(BlogSnippets);
