import React, { Component } from "react";
import ReportModelApiService from "../services/report-model.service";

export default class ReportModel extends Component {
  constructor(props) {
    super(props);
    this.onChangeTitle = this.onChangeTitle.bind(this);
    this.onChangeLayer = this.onChangeLayer.bind(this);
    this.getReportModel = this.getReportModel.bind(this);
    this.updateReportModel = this.updateReportModel.bind(this);
    this.deleteReportModel = this.deleteReportModel.bind(this);

    this.state = {
      currentReportModel: {
        id: null,
        title: "",
        layer: ""
      },
      message: ""
    };
  }

  componentDidMount() {
    this.getReportModel(this.props.match.params.id);
  }

  onChangeTitle(e) {
    const title = e.target.value;

    this.setState(function(prevState) {
      return {
        currentReportModel: {
          ...prevState.currentReportModel,
          title: title
        }
      };
    });
  }

  onChangeLayer(e) {
    const layer = e.target.value;
    
    this.setState(prevState => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        layer: layer
      }
    }));
  }

  getReportModel(id) {
    ReportModelApiService.get(id)
      .then(response => {
        this.setState({
          currentReportModel: response.data
        });
        console.log(response.data);
      })
      .catch(e => {
        console.log(e);
      });
  }

  updateReportModel() {
    ReportModelApiService.update(
      this.state.currentReportModel.id,
      this.state.currentReportModel
    )
      .then(response => {
        console.log(response.data);
        this.setState({
          message: "The Report Model was updated successfully!"
        });
      })
      .catch(e => {
        console.log(e);
      });
  }

  deleteReportModel() {    
    ReportModelApiService.delete(this.state.currentReportModel.id)
      .then(response => {
        console.log(response.data);
        this.props.history.push('/reportmodels')
      })
      .catch(e => {
        console.log(e);
      });
  }

  render() {
    const { currentReportModel } = this.state;

    return (
      <div>
        {currentReportModel ? (
          <div className="edit-form">
            <h4>Report Model</h4>
            <form>
              <div className="form-group">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  className="form-control"
                  id="title"
                  value={currentReportModel.title}
                  onChange={this.onChangeTitle}
                />
              </div>
              <div className="form-group">
                <label htmlFor="layer">Layer</label>
                <input
                  type="text"
                  className="form-control"
                  id="layer"
                  value={currentReportModel.layer}
                  onChange={this.onChangeLayer}
                />
              </div>
            </form>

            <button
              className="badge badge-danger mr-2"
              onClick={this.deleteReportModel}
            >
              Delete
            </button>

            <button
              type="submit"
              className="badge badge-success"
              onClick={this.updateReportModel}
            >
              Update
            </button>
            <p>{this.state.message}</p>
          </div>
        ) : (
          <div>
            <br />
            <p>Please click on a Report Model...</p>
          </div>
        )}
      </div>
    );
  }
}
