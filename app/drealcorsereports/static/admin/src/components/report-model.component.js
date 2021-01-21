import React, { Component } from "react";
import ReportModelApiService from "../services/report-model.service";

export default class ReportModel extends Component {
  constructor(props) {
    super(props);
    this.onChangeTitle = this.onChangeTitle.bind(this);
    this.onChangeLayer = this.onChangeLayer.bind(this);
    this.onChangeProperty = this.onChangeProperty.bind(this);
    this.getReportModel = this.getReportModel.bind(this);
    this.updateReportModel = this.updateReportModel.bind(this);
    this.deleteReportModel = this.deleteReportModel.bind(this);

    this.state = {
      currentReportModel: {
        id: null,
        title: "",
        layer: "",
        properties: []
      },
      message: ""
    };
  }

  componentDidMount() {
    this.getReportModel(this.props.currentReportModel.id);
  }

  componentDidUpdate(prevProps) {
    if(prevProps.currentReportModel.id!==this.props.currentReportModel.id){
      this.getReportModel(this.props.currentReportModel.id);
    }
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

  onChangeProperty(edit, index, e) {
    this.setState(prevState => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        properties: prevState.currentReportModel.properties.map((property, id) => {
          const returnProperty = {...property}
          if (id === index) {
            switch (edit){
              case 'name':
                returnProperty.name = e.target.value
                break
              case 'type':
                returnProperty.type = e.target.value
                break
              case 'required':
                returnProperty.required = e.target.checked
                break
              default:
            }
          }
          return returnProperty
        })
      }
    }));
  }

  addProperty() {
    const properties = this.state.currentReportModel.properties;
    properties.push({
      name: "",
      type: "",
      required: false
    })
    this.setState(prevState => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        properties
      }
    }))
  }

  deleteProperty(index, e) {
    e.preventDefault()
    this.setState(prevState => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        properties: prevState.currentReportModel.properties.filter((property, id) => {
          return id !== index
        })
      }
    }))
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
    this.props.onUpdateReportModel(this.state.currentReportModel);
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

              <label htmlFor="properties">Form properties</label>
              <div id="properties" className="form-group">
                {currentReportModel.properties &&
                  currentReportModel.properties.map((property, index) => (
                  <div key={index} className="row">
                    <div className="col-4">
                      <label>Property name</label>
                      <input
                        type="text"
                        className="form-control mb-2"
                        value={property.name}
                        onChange={(e) => this.onChangeProperty('name', index, e)}
                      />
                    </div>
                    <div className="col-4">
                      <label>Property type</label>
                      <select 
                        className="form-control mb-2" value={property.type} onChange={(e) => this.onChangeProperty('type', index, e)}>
                        <option value=""></option>
                        <option value="string">string</option>
                        <option value="number">number</option>
                      </select>
                    </div>
                    <div className="col-2">
                      <label>Required</label>
                      <input
                        className="form-check"
                        type="checkbox" checked={property.required} onChange={(e) => this.onChangeProperty('required', index, e)}/>
                    </div>
                    <div className="col-1">
                      <button
                        className="btn btn-danger mt-4"
                        onClick={(e) => this.deleteProperty(index, e)}
                      >
                        -
                      </button>
                    </div>
                  </div>
                  ))}
              </div>

            </form>

            <button
              className="btn btn-danger mr-2"
              onClick={this.deleteReportModel}
            >
              Delete
            </button>

            <button
              type="submit"
              className="btn btn-success mr-2"
              onClick={this.updateReportModel}
            >
              Update
            </button>

            <button
              type="submit"
              className="btn btn-warning"
              onClick={(e) => this.addProperty()}
            >
              Add Property
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
