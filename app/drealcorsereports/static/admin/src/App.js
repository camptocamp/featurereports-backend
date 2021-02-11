import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import './App.css';
import ReportModelList from './components/report-model-list.component';
import ReportModel from './components/report-model.component';
import ReportModelApiService from './services/report-model.service';
import axios from 'axios';
import { getErrorMessage } from './http-common';

class App extends Component {
  constructor() {
    super();

    this.state = {
      reportModels: [],
      newReportModel: null,
      currentReportModel: null,
      searchTitle: '',
      errorMessage: '',
    };

    this.source = axios.CancelToken.source();
  }

  componentDidMount() {
    this.retrieveReportModels();
  }

  componentWillUnmount() {
    if (this.source) {
      this.source.cancel('Component got unmounted');
    }
  }

  retrieveReportModels() {
    ReportModelApiService.getAll(this.source.token)
      .then((response) => {
        this.setState({
          reportModels: response.data,
        });
      })
      .catch((e) => {
        this.setState({
          errorMessage: getErrorMessage(e),
        });
      });
  }

  refreshList() {
    this.retrieveReportModels();
    this.clearSelection();
  }

  clearSelection() {
    this.setState({
      newReportModel: null,
      currentReportModel: null,
    });
  }

  editReportModel(reportModel) {
    this.setState({
      currentReportModel: reportModel,
    });
  }

  addReportModel() {
    this.setState({
      newReportModel: {
        id: null,
        name: '',
        layer_id: '',
        custom_field_schema: [],
      },
      currentReportModel: null,
    });
  }

  render() {
    const { reportModels, newReportModel, currentReportModel } = this.state;

    return (
      <div>
        <nav className="navbar navbar-expand navbar-dark bg-dark">
          <div className="navbar-brand">drealcorse-reports</div>
          <button
            onClick={() => this.addReportModel()}
            className="btn btn-warning position-absolute"
            style={{ right: 10 }}
          >
            Ajouter un modèle
          </button>
        </nav>

        <div className="container mt-3">
          {currentReportModel ? (
            <ReportModel
              key="edit"
              currentReportModel={currentReportModel}
              onReportModelChange={(e) => this.refreshList(e)}
              onCancel={(e) => this.clearSelection(e)}
            />
          ) : newReportModel ? (
            <ReportModel
              key="add"
              currentReportModel={newReportModel}
              onReportModelChange={(e) => this.refreshList(e)}
              onCancel={(e) => this.clearSelection(e)}
            />
          ) : (
            <div className="col-md-12">
              <ReportModelList
                reportModels={reportModels}
                editReportModel={(e) => this.editReportModel(e)}
              />
              <p className="mt-2 text-danger">{this.state.errorMessage}</p>
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default App;
