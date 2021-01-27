import React, { Component } from 'react';
import ReportModelApiService from '../services/report-model.service';

export default class ReportModel extends Component {
  constructor(props) {
    super(props);
    this.onChangeName = this.onChangeName.bind(this);
    this.onChangeLayer = this.onChangeLayer.bind(this);
    this.onChangeField = this.onChangeField.bind(this);
    this.getReportModel = this.getReportModel.bind(this);
    this.submitReportModel = this.submitReportModel.bind(this);
    this.createReportModel = this.createReportModel.bind(this);
    this.updateReportModel = this.updateReportModel.bind(this);
    this.deleteReportModel = this.deleteReportModel.bind(this);

    this.state = {
      currentReportModel: {
        id: null,
        name: '',
        layer_id: '',
        custom_field_schema: [],
        created_at: '',
        created_by: '',
        updated_at: '',
        updated_by: '',
      },
      message: '',
    };
  }

  componentDidMount() {
    if (this.props.currentReportModel.id !== null) {
      this.getReportModel(this.props.currentReportModel.id);
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.currentReportModel.id !== this.props.currentReportModel.id) {
      this.getReportModel(this.props.currentReportModel.id);
    }
  }

  onChangeName(e) {
    const name = e.target.value;

    this.setState(function (prevState) {
      return {
        currentReportModel: {
          ...prevState.currentReportModel,
          name: name,
        },
      };
    });
  }

  onChangeLayer(e) {
    const layer_id = e.target.value;

    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        layer_id: layer_id,
      },
    }));
  }

  onChangeField(edit, index, e) {
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_field_schema: prevState.currentReportModel.custom_field_schema.map(
          (field, id) => {
            const returnField = { ...field };
            if (id === index) {
              switch (edit) {
                case 'name':
                  returnField.name = e.target.value;
                  break;
                case 'type':
                  returnField.type = e.target.value;
                  break;
                case 'required':
                  returnField.required = e.target.checked;
                  break;
                default:
              }
            }
            return returnField;
          }
        ),
      },
    }));
  }

  addField() {
    const custom_field_schema = this.state.currentReportModel.custom_field_schema;
    custom_field_schema.push({
      name: '',
      type: '',
      required: false,
    });
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_field_schema,
      },
    }));
  }

  deleteField(index, e) {
    e.preventDefault();
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_field_schema: prevState.currentReportModel.custom_field_schema.filter(
          (field, id) => {
            return id !== index;
          }
        ),
      },
    }));
  }

  getReportModel(id) {
    ReportModelApiService.get(id)
      .then((response) => {
        this.setState({
          currentReportModel: response.data,
        });
        console.log(response.data);
      })
      .catch((e) => {
        console.log(e);
      });
  }

  submitReportModel() {
    if (this.props.currentReportModel.id !== null) {
      this.updateReportModel();
    } else {
      this.createReportModel();
    }
  }

  createReportModel() {
    var data = {
      name: this.state.currentReportModel.name,
      layer_id: this.state.currentReportModel.layer_id,
      custom_field_schema: this.state.currentReportModel.custom_field_schema,
    };

    ReportModelApiService.create(data)
      .then((response) => {
        this.setState({
          id: response.data.id,
          name: response.data.name,
          layer_id: response.data.layer_id,
          custom_field_schema: response.data.custom_field_schema,
        });
        console.log(response.data);
        this.props.onReportModelChange();
      })
      .catch((e) => {
        console.log(e);
      });
  }

  updateReportModel() {
    ReportModelApiService.update(
      this.state.currentReportModel.id,
      this.state.currentReportModel
    )
      .then((response) => {
        console.log(response.data);
        this.setState({
          message: 'The Report Model was updated successfully!',
        });
        this.props.onReportModelChange();
      })
      .catch((e) => {
        console.log(e);
      });
  }

  deleteReportModel() {
    ReportModelApiService.delete(this.state.currentReportModel.id)
      .then((response) => {
        console.log(response.data);
        this.props.onReportModelChange();
      })
      .catch((e) => {
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
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="name"
                  value={currentReportModel.name}
                  onChange={this.onChangeName}
                />
              </div>
              <div className="form-group">
                <label htmlFor="layer_id">Layer</label>
                <input
                  type="text"
                  className="form-control"
                  id="layer_id"
                  value={currentReportModel.layer_id}
                  onChange={this.onChangeLayer}
                />
              </div>

              <label htmlFor="custom_field_schema">Form fields</label>
              <div id="custom_field_schema" className="form-group">
                {currentReportModel.custom_field_schema &&
                  currentReportModel.custom_field_schema.map((field, index) => (
                    <div key={index} className="row">
                      <div className="col-4">
                        <label>Field name</label>
                        <input
                          type="text"
                          className="form-control mb-2"
                          value={field.name}
                          onChange={(e) =>
                            this.onChangeField('name', index, e)
                          }
                        />
                      </div>
                      <div className="col-4">
                        <label>Field type</label>
                        <select
                          className="form-control mb-2"
                          value={field.type}
                          onChange={(e) =>
                            this.onChangeField('type', index, e)
                          }
                        >
                          <option value=""></option>
                          <option value="string">string</option>
                          <option value="number">number</option>
                        </select>
                      </div>
                      <div className="col-2">
                        <label>Required</label>
                        <input
                          className="form-check"
                          type="checkbox"
                          checked={field.required}
                          onChange={(e) =>
                            this.onChangeField('required', index, e)
                          }
                        />
                      </div>
                      <div className="col-1">
                        <button
                          className="btn btn-danger mt-4"
                          onClick={(e) => this.deleteField(index, e)}
                        >
                          -
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </form>

            {currentReportModel.id && (
              <button
                className="btn btn-danger mr-2"
                onClick={() => {
                  if (
                    window.confirm(
                      'Are you sure you wish to delete the report model?'
                    )
                  )
                    this.deleteReportModel();
                }}
              >
                Delete
              </button>
            )}

            <button
              type="submit"
              className="btn btn-success mr-2"
              onClick={() => {
                if (window.confirm('Please confirm to save your changes'))
                  this.submitReportModel();
              }}
            >
              Save
            </button>

            <button
              type="submit"
              className="btn btn-warning"
              onClick={(e) => this.addField()}
            >
              Add Field
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
