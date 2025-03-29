import { createRoot } from "react-dom/client";
import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router }  from "react-router-dom";
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';

const root = createRoot(document.getElementById('root'));

root.render(<Router>
  <App />
</Router>);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
