import React, { Component } from 'react';
import ReportModelApiService from '../services/report-model.service';
import axios from 'axios';

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
    this.validateReportModel = this.validateReportModel.bind(this);

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
      formWarnings: {
        name: '',
        layer: '',
        fields: '',
        fieldName: {},
        fieldType: {},
      },
      errorMessage: '',
    };

    this.source = axios.CancelToken.source();
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

  componentWillUnmount() {
    if (this.source) {
      this.source.cancel('Component got unmounted');
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
        formWarnings: {
          ...prevState.formWarnings,
          name: name ? '' : prevState.formWarnings.name,
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
      formWarnings: {
        ...prevState.formWarnings,
        layer: layer_id ? '' : prevState.formWarnings.layer,
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
      formWarnings: {
        ...prevState.formWarnings,
        fieldName: Object.values(prevState.formWarnings.fieldName).map(
          (value, id) => {
            return edit === 'name' && e.target.value && id === index
              ? ''
              : value;
          }
        ),
        fieldType: Object.values(prevState.formWarnings.fieldType).map(
          (value, id) => {
            return edit === 'type' && e.target.value && id === index
              ? ''
              : value;
          }
        ),
      },
    }));
  }

  addField() {
    const custom_field_schema = this.state.currentReportModel
      .custom_field_schema;
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
      formWarnings: {
        ...prevState.formWarnings,
        fields:
          prevState.currentReportModel.custom_field_schema.length > 0
            ? ''
            : prevState.formWarnings.fields,
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
    ReportModelApiService.get(id, this.source.token)
      .then((response) => {
        this.setState({
          currentReportModel: response.data,
        });
      })
      .catch((e) => {
        console.log(e);
      });
  }

  submitReportModel() {
    if (this.validateReportModel()) {
      if (this.props.currentReportModel.id !== null) {
        this.updateReportModel();
      } else {
        this.createReportModel();
      }
    }
  }

  createReportModel() {
    var data = {
      name: this.state.currentReportModel.name,
      layer_id: this.state.currentReportModel.layer_id,
      custom_field_schema: this.state.currentReportModel.custom_field_schema,
    };

    ReportModelApiService.create(data, this.source.token)
      .then((response) => {
        this.setState({
          id: response.data.id,
          name: response.data.name,
          layer_id: response.data.layer_id,
          custom_field_schema: response.data.custom_field_schema,
        });
        this.props.onReportModelChange();
      })
      .catch((e) => {
        this.setState({
          errorMessage: e.response.data.errors[0].description[0],
        });
      });
  }

  updateReportModel() {
    ReportModelApiService.update(
      this.state.currentReportModel.id,
      this.state.currentReportModel,
      this.source.token
    )
      .then(() => {
        this.props.onReportModelChange();
      })
      .catch((e) => {
        this.setState({
          errorMessage: e.response.data.errors[0].description[0],
        });
      });
  }

  deleteReportModel() {
    ReportModelApiService.delete(
      this.state.currentReportModel.id,
      this.source.token
    )
      .then(() => {
        this.props.onReportModelChange();
      })
      .catch((e) => {
        console.log(e);
      });
  }

  validateReportModel() {
    let formWarnings = {
      name: '',
      type: '',
      fields: '',
      fieldName: {},
      fieldType: {},
    };
    let valid = true;
    if (this.state.currentReportModel.name === '') {
      formWarnings.name = 'Please indicate a name';
      valid = false;
    }
    if (this.state.currentReportModel.layer_id === '') {
      formWarnings.layer = 'Please indicate a layer';
      valid = false;
    }
    if (this.state.currentReportModel.custom_field_schema.length === 0) {
      formWarnings.fields = 'Please add at least one field';
      valid = false;
    }
    for (const f in this.state.currentReportModel.custom_field_schema) {
      if (this.state.currentReportModel.custom_field_schema[f].name === '') {
        formWarnings.fieldName[f] = 'required';
        valid = false;
      }
      if (this.state.currentReportModel.custom_field_schema[f].type === '') {
        formWarnings.fieldType[f] = 'required';
        valid = false;
      }
    }
    this.setState({
      formWarnings,
    });
    return valid;
  }

  render() {
    const { currentReportModel, formWarnings } = this.state;

    return (
      <div>
        {currentReportModel && (
          <div className="edit-form">
            <h4>Modèle de rapport</h4>
            <form>
              <div className="form-group">
                <label htmlFor="name">Titre*</label>
                <span style={{ color: 'red', float: 'right' }}>
                  {formWarnings['name']}
                </span>
                <input
                  required
                  type="text"
                  className="form-control"
                  id="name"
                  value={currentReportModel.name}
                  onChange={this.onChangeName}
                />
              </div>
              <div className="form-group">
                <label htmlFor="layer_id">Couche associée*</label>
                <span style={{ color: 'red', float: 'right' }}>
                  {formWarnings['layer']}
                </span>
                <input
                  type="text"
                  className="form-control"
                  id="layer_id"
                  value={currentReportModel.layer_id}
                  onChange={this.onChangeLayer}
                />
              </div>

              <label htmlFor="custom_field_schema">Champs de formulaire</label>
              <span style={{ color: 'red', float: 'right' }}>
                {formWarnings['fields']}
              </span>
              <div id="custom_field_schema" className="form-group">
                {currentReportModel.custom_field_schema &&
                  currentReportModel.custom_field_schema.map((field, index) => (
                    <div key={index} className="row">
                      <div className="col-4">
                        <label htmlFor="field_name">Libellé*</label>
                        <input
                          type="text"
                          className="form-control mb-2"
                          value={field.name}
                          id="field_name"
                          onChange={(e) => this.onChangeField('name', index, e)}
                        />
                        {formWarnings['fieldName'] && (
                          <span style={{ color: 'red' }}>
                            {formWarnings['fieldName'][index]}
                          </span>
                        )}
                      </div>
                      <div className="col-4">
                        <label htmlFor="field_type">Type*</label>
                        <select
                          className="form-control mb-2"
                          value={field.type}
                          id="field_type"
                          onChange={(e) => this.onChangeField('type', index, e)}
                        >
                          <option value=""></option>
                          <option value="string">string</option>
                          <option value="number">number</option>
                        </select>
                        {formWarnings['fieldType'] && (
                          <span style={{ color: 'red' }}>
                            {formWarnings['fieldType'][index]}
                          </span>
                        )}
                      </div>
                      <div className="col-2">
                        <label htmlFor="field_required">Réquis</label>
                        <input
                          className="form-check"
                          type="checkbox"
                          checked={field.required}
                          id="field_required"
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
                Supprimer
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
              Sauvegarder
            </button>

            <button
              type="submit"
              className="btn btn-warning"
              onClick={(e) => this.addField()}
            >
              Ajouter un champ
            </button>
            <p className="mt-2 text-danger">{this.state.errorMessage}</p>
          </div>
        )}
      </div>
    );
  }
}
