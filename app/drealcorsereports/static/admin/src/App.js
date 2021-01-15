import React, { Component } from "react";
import { Switch, Route, Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import AddReportModel from "./components/add-report-model.component";
import ReportModelList from "./components/report-model-list.component";
import ReportModel from "./components/report-model.component";

class App extends Component {
  render() {
    // fetch('/api')
    // .then(response => response.json())
    // .then(data => console.log(data));
    return (
      <div>
        <nav className="navbar navbar-expand navbar-dark bg-dark">
          <a href="/reportmodels" className="navbar-brand">
            drealcorse-reports
          </a>
          <div className="navbar-nav mr-auto">
            <li className="nav-item">
              <Link to={"/reportmodels"} className="nav-link">
                Report Models
              </Link>
            </li>
            <li className="nav-item">
              <Link to={"/add"} className="nav-link">
                Add
              </Link>
            </li>
          </div>
        </nav>

        <div className="container mt-3">
          <Switch>
            <Route exact path={["/", "/reportmodels"]} component={ReportModelList} />
            <Route exact path="/add" component={AddReportModel} />
            <Route path="/reportmodels/:id" component={ReportModel} />
          </Switch>
        </div>
      </div>
    );
  }
}

export default App;
