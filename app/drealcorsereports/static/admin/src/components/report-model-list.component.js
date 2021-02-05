import React, { Component } from 'react';
import ReportModelApiService from '../services/report-model.service';
import ReportModel from './report-model.component';
import axios from 'axios';

export default class ReportModelList extends Component {
  constructor(props) {
    super(props);
    this.retrieveReportModels = this.retrieveReportModels.bind(this);
    this.refreshList = this.refreshList.bind(this);
    this.setActiveReportModel = this.setActiveReportModel.bind(this);

    this.state = {
      reportModels: [],
      newReportModel: null,
      currentReportModel: null,
      currentIndex: -1,
      searchTitle: '',
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
        console.log(e);
      });
  }

  refreshList() {
    this.retrieveReportModels();
    this.setState({
      newReportModel: null,
      currentReportModel: null,
      currentIndex: -1,
    });
  }

  setActiveReportModel(reportModel, index) {
    this.setState({
      currentReportModel: reportModel,
      currentIndex: index,
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
      currentIndex: -1,
    });
  }

  render() {
    const {
      reportModels,
      newReportModel,
      currentReportModel,
      currentIndex,
    } = this.state;

    return (
      <div className="list row">
        <div className="col-md-6">
          <h4>Liste des modèles de rapport</h4>

          <ul className="list-group">
            {reportModels &&
              reportModels.map((reportModel, index) => (
                <li
                  className={
                    'list-group-item ' +
                    (index === currentIndex ? 'active' : '')
                  }
                  onClick={() => this.setActiveReportModel(reportModel, index)}
                  key={index}
                >
                  {reportModel.name}
                </li>
              ))}
          </ul>
        </div>
        <div className="col-md-6">
          <button
            onClick={() => this.addReportModel()}
            className="btn btn-warning position-absolute"
            style={{ right: 0 }}
          >
            Ajouter un modèle
          </button>
          {currentReportModel ? (
            <ReportModel
              key="edit"
              currentReportModel={currentReportModel}
              onReportModelChange={this.refreshList}
            />
          ) : newReportModel && (
            <ReportModel
              key="add"
              currentReportModel={newReportModel}
              onReportModelChange={this.refreshList}
            />
          )}
        </div>
      </div>
    );
  }
}
