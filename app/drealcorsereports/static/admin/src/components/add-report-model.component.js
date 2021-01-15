import React, { Component } from "react";
import ReportModelApiService from "../services/report-model.service";

export default class AddReportModel extends Component {
  constructor(props) {
    super(props);
    this.onChangeTitle = this.onChangeTitle.bind(this);
    this.onChangeLayer = this.onChangeLayer.bind(this);
    this.saveReportModel = this.saveReportModel.bind(this);
    this.newReportModel = this.newReportModel.bind(this);

    this.state = {
      id: null,
      title: "",
      layer: "",
      submitted: false
    };
  }

  onChangeTitle(e) {
    this.setState({
      title: e.target.value
    });
  }

  onChangeLayer(e) {
    this.setState({
      layer: e.target.value
    });
  }

  saveReportModel() {
    var data = {
      title: this.state.title,
      layer: this.state.layer
    };

    ReportModelApiService.create(data)
      .then(response => {
        this.setState({
          id: response.data.id,
          title: response.data.title,
          layer: response.data.layer,
          submitted: true
        });
        console.log(response.data);
      })
      .catch(e => {
        console.log(e);
      });
  }

  newReportModel() {
    this.setState({
      id: null,
      title: "",
      layer: "",
      submitted: false
    });
  }

  render() {
    return (
      <div className="submit-form">
        {this.state.submitted ? (
          <div>
            <h4>Report Model added successfully!</h4>
            <button className="btn btn-success" onClick={this.newReportModel}>
              Add
            </button>
          </div>
        ) : (
          <div>
            <div className="form-group">
              <label htmlFor="title">Title</label>
              <input
                type="text"
                className="form-control"
                id="title"
                required
                value={this.state.title}
                onChange={this.onChangeTitle}
                name="title"
              />
            </div>

            <div className="form-group">
              <label htmlFor="layer">layer</label>
              <input
                type="text"
                className="form-control"
                id="layer"
                required
                value={this.state.layer}
                onChange={this.onChangeLayer}
                name="layer"
              />
            </div>

            <button onClick={this.saveReportModel} className="btn btn-success">
              Submit
            </button>
          </div>
        )}
      </div>
    );
  }
}
