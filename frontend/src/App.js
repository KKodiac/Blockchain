import logo from './logo.svg';
import './App.css';
import React, { Component } from 'react';
import Status from './components/status';
import Send from './components/send';
import Transactions from './components/transactions';
import axios from 'axios';

const endpoint = '/mine_block'

class App extends Component {
  constructor(props){
    super(
      props
    );
  }

  componentWillMount() {
    axios.get(endpoint)
  }
  render(){
    return(
      <div className="App">
          <Status/>
          <Send/>
          <Transactions/>
      </div>
    );
  }
}

export default App;
