import React, { Component } from 'react';
import ReportModelApiService from '../services/report-model.service';
import axios from 'axios';
import { getErrorMessage } from '../http-common';
import { FaMinus } from 'react-icons/fa';
import { FaPlus } from 'react-icons/fa';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import './report-model.component.css';

const defaultReportModel = {
  id: null,
  name: '',
  layer_id: '',
  custom_field_schema: [],
  created_at: '',
  created_by: '',
  updated_at: '',
  updated_by: '',
};

const defaultFormWarnings = {
  name: '',
  layer: '',
  fields: '',
  fieldName: {},
  fieldType: {},
};

const defaultCustomField = {
  name: '',
  type: '',
  valueList: [],
  required: false,
};

export default class ReportModel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      currentReportModel: defaultReportModel,
      formWarnings: defaultFormWarnings,
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

    this.setState((prevState) => {
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

  onChangeField(propertyName, value, index) {
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_field_schema: prevState.currentReportModel.custom_field_schema.map(
          (field, id) => {
            const returnField = { ...field };
            if (id === index) {
              switch (propertyName) {
                case 'name':
                  returnField.name = value;
                  break;
                case 'type':
                  returnField.type = value;
                  break;
                case 'valueList' :
                  returnField.valueList = value;
                  break;
                case 'required':
                  returnField.required = value;
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
            return propertyName === 'name' && value && id === index
              ? ''
              : value;
          }
        ),
        fieldType: Object.values(prevState.formWarnings.fieldType).map(
          (value, id) => {
            return propertyName === 'type' && value && id === index
              ? ''
              : value;
          }
        ),
      },
    }));
  }

  addField(e) {
    e.preventDefault();
    const custom_field_schema = this.state.currentReportModel
      .custom_field_schema;
    custom_field_schema.push(defaultCustomField);
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
        this.setState({
          errorMessage: getErrorMessage(e),
        });
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
          errorMessage: getErrorMessage(e),
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
          errorMessage: getErrorMessage(e),
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
        this.setState({
          errorMessage: getErrorMessage(e),
        });
      });
  }

  validateReportModel() {
    let formWarnings = defaultFormWarnings;
    let valid = true;
    if (this.state.currentReportModel.name === '') {
      formWarnings.name = 'Veuillez indiquer un titre';
      valid = false;
    }
    if (this.state.currentReportModel.layer_id === '') {
      formWarnings.layer = 'Veuillez indiquer une couche';
      valid = false;
    }
    if (this.state.currentReportModel.custom_field_schema.length === 0) {
      formWarnings.fields = 'Veuillez ajouter au moins un champ';
      valid = false;
    }
    for (const f in this.state.currentReportModel.custom_field_schema) {
      if (this.state.currentReportModel.custom_field_schema[f].name === '') {
        formWarnings.fieldName[f] = 'obligatoire';
        valid = false;
      }
      if (this.state.currentReportModel.custom_field_schema[f].type === '') {
        formWarnings.fieldType[f] = 'obligatoire';
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
                  onChange={(e) => this.onChangeName(e)}
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
                  onChange={(e) => this.onChangeLayer(e)}
                />
              </div>

              <label htmlFor="custom_field_schema">Champs de formulaire</label>
              <span style={{ color: 'red', float: 'right' }}>
                {formWarnings['fields']}
              </span>
              <div id="custom_field_schema" className="form-group">
                {currentReportModel.custom_field_schema.length !== 0 ? (
                  currentReportModel.custom_field_schema.map((field, index) => (
                    <div key={index} className="row">
                      <div className="col-4">
                        <label htmlFor="field_name">Libellé*</label>
                        <input
                          type="text"
                          className="form-control mb-2"
                          value={field.name}
                          id="field_name"
                          onChange={(e) => this.onChangeField('name', e.target.value, index)}
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
                          onChange={(e) => this.onChangeField('type', e.target.value, index)}
                        >
                          <option value=""></option>
                          <option value="string">texte</option>
                          <option value="array-string">
                            liste déroulante
                          </option>
                          <option value="number">numérique</option>
                          <option value="boolean">boolean</option>
                          <option value="date">date</option>
                          <option value="file">photo</option>
                        </select>
                        {currentReportModel.custom_field_schema[index].type === "array-string" && (
                          <TagsInput 
                            value={currentReportModel.custom_field_schema[index].valueList} 
                            inputProps={{placeholder:'choix possibles'}}
                            onChange={(e) => this.onChangeField('valueList', e, index)}
                          />
                        )}
                        
                        {formWarnings['fieldType'] && (
                          <span style={{ color: 'red' }}>
                            {formWarnings['fieldType'][index]}
                          </span>
                        )}
                      </div>
                      <div className="col-2">
                        <label htmlFor="field_required">Requis</label>
                        <input
                          className="form-check"
                          type="checkbox"
                          checked={field.required}
                          id="field_required"
                          onChange={(e) =>
                            this.onChangeField('required', e.target.checked, index)
                          }
                        />
                      </div>
                      <div className="col-1">
                        <button
                          className="btn btn-danger mt-4"
                          onClick={(e) => this.deleteField(index, e)}
                        >
                          <FaMinus />
                        </button>
                      </div>
                      <div className="col-1">
                        {index ===
                          currentReportModel.custom_field_schema.length - 1 && (
                          <button
                            className="btn btn-success mt-4"
                            onClick={(e) => this.addField(e)}
                          >
                            <FaPlus />
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <button
                    className="btn btn-success"
                    onClick={(e) => this.addField(e)}
                  >
                    <FaPlus />
                  </button>
                )}
              </div>
            </form>

            {currentReportModel.id && (
              <button
                className="btn btn-danger mr-2"
                onClick={() => {
                  if (
                    window.confirm(
                      'Veuillez confirmer la suppression du modèle de rapport'
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
                if (window.confirm('Veuillez confirmer vos modifications'))
                  this.submitReportModel();
              }}
            >
              Sauvegarder
            </button>

            <button
              type="submit"
              className="btn btn-secondary mr-2"
              onClick={() => {
                this.props.onCancel();
              }}
            >
              Annuler
            </button>

            <p className="mt-2 text-danger">{this.state.errorMessage}</p>
          </div>
        )}
      </div>
    );
  }
}
