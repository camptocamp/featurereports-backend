import React, { Component } from "react";
import ReportModelApiService from "../services/report-model.service";
import { Link } from "react-router-dom";

export default class ReportModelList extends Component {
  constructor(props) {
    super(props);
    this.onChangeSearchTitle = this.onChangeSearchTitle.bind(this);
    this.retrieveReportModels = this.retrieveReportModels.bind(this);
    this.refreshList = this.refreshList.bind(this);
    this.setActiveReportModel = this.setActiveReportModel.bind(this);
    // this.searchTitle = this.searchTitle.bind(this);

    this.state = {
      reportModels: [],
      currentReportModel: null,
      currentIndex: -1,
      searchTitle: ""
    };
  }

  componentDidMount() {
    this.retrieveReportModels();
  }

  onChangeSearchTitle(e) {
    const searchTitle = e.target.value;

    this.setState({
      searchTitle: searchTitle
    });
  }

  retrieveReportModels() {
    ReportModelApiService.getAll()
      .then(response => {
        this.setState({
          reportModels: response.data
        });
      })
      .catch(e => {
        console.log(e);
      });
  }

  refreshList() {
    this.retrieveReportModels();
    this.setState({
      currentReportModel: null,
      currentIndex: -1
    });
  }

  setActiveReportModel(reportModel, index) {
    this.setState({
      currentReportModel: reportModel,
      currentIndex: index
    });
  }

  // searchTitle() {
  //   ReportModelApiService.findByTitle(this.state.searchTitle)
  //     .then(response => {
  //       this.setState({
  //         reportModels: response.data
  //       });
  //       console.log(response.data);
  //     })
  //     .catch(e => {
  //       console.log(e);
  //     });
  // }

  render() {
    const { searchTitle, reportModels, currentReportModel, currentIndex } = this.state;

    return (
      <div className="list row">
        {/* <div className="col-md-8">
          <div className="input-group mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="Search by title"
              value={searchTitle}
              onChange={this.onChangeSearchTitle}
            />
            <div className="input-group-append">
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={this.searchTitle}
              >
                Search
              </button>
            </div>
          </div>
        </div> */}
        <div className="col-md-6">
          <h4>Report Model List</h4>

          <ul className="list-group">
            {reportModels &&
              reportModels.map((reportModel, index) => (
                <li
                  className={
                    "list-group-item " +
                    (index === currentIndex ? "active" : "")
                  }
                  onClick={() => this.setActiveReportModel(reportModel, index)}
                  key={index}
                >
                  {reportModel.title}
                </li>
              ))}
          </ul>
        </div>
        <div className="col-md-6">
          {currentReportModel ? (
            <div>
              <h4>Report Model</h4>
              <div>
                <label>
                  <strong>Title:</strong>
                </label>{" "}
                {currentReportModel.title}
              </div>
              <div>
                <label>
                  <strong>Layer:</strong>
                </label>{" "}
                {currentReportModel.layer}
              </div>

              <Link
                to={"/reportModels/" + currentReportModel.id}
                className="badge badge-warning"
              >
                Edit
              </Link>
            </div>
          ) : (
            <div>
              <br />
              <p>Please click on a Report Model...</p>
            </div>
          )}
        </div>
      </div>
    );
  }
}
