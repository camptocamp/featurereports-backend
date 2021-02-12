import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import ReportModelList from './components/report-model-list.component';

class App extends Component {
  render() {
    return (
      <div>
        <nav className="navbar navbar-expand navbar-dark bg-dark">
          <div className="navbar-brand">drealcorse-reports</div>
        </nav>

        <div className="container mt-3">
          <ReportModelList />
        </div>
      </div>
    );
  }
}

export default App;
