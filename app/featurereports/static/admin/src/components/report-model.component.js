import React, { Component } from 'react';
import ReportModelApiService from '../services/report-model.service';
import LayerApiService from '../services/layers.service';
import axios from 'axios';
import { getErrorMessage } from '../http-common';
import { FaMinus } from 'react-icons/fa';
import { FaPlus } from 'react-icons/fa';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Select from 'react-select';
import './report-model.component.css';

const defaultReportModel = {
  id: null,
  name: '',
  title: '',
  layer_id: '',
  custom_fields: [],
  created_at: '',
  created_by: '',
  updated_at: '',
  updated_by: '',
};

const defaultFormWarnings = {
  title: '',
  layer: '',
  fields: '',
  name: '',
  fieldTitle: {},
  fieldType: {},
};

const defaultCustomField = {
  title: '',
  name: '',
  type: '',
  enum: [],
  required: false,
};

export default class ReportModel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      currentReportModel: defaultReportModel,
      layers: [],
      formWarnings: defaultFormWarnings,
      errorMessage: '',
      isNew: true
    };

    this.source = axios.CancelToken.source();
  }

  componentDidMount() {
    if (this.props.currentReportModel.id !== null) {
      this.getReportModel(this.props.currentReportModel.id);
    }
    this.getLayers();
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

  onNameChange(e) {
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

  onTitleChange(e) {
    const title = e.target.value;
    const name = this.state.isNew ? this.createName(title) : this.state.currentReportModel.name;

    this.setState((prevState) => {
      return {
        currentReportModel: {
          ...prevState.currentReportModel,
          title: title,
          name: name
        },
        formWarnings: {
          ...prevState.formWarnings,
          title: title ? '' : prevState.formWarnings.title,
        },
      };
    });
  }

  getLayers() {
    LayerApiService.getLayers()
      .then((response) => {
        this.setState({
          layers: response.data,
        });
      })
      .catch((e) => {
        this.setState({
          errorMessage: getErrorMessage(e),
        });
      });
  }

  layerOption(layer_id) {
    return {label: layer_id, value: layer_id};
  }

  onLayerChange(e) {
    const layer_id = e.value;

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

  createName(title) {
    // normalize title to match name regex
    return title.normalize("NFD").replace(/ /g, "_").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z_0-9]/g, '');
  }

  createNameWithSuffix(title, length = 8) {
    let name = this.createName(title)  + '_';
    
    // add a randomized suffix in case two fields would have similar titles (ex : "Field" and "field") 
    const chars = 'abcdefghijklmnopqrstuvwxyz_';
    for (let i = 0; i < length; i++) {
        name += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return name;
  }

  onFieldChange(propertyName, value, index) {
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_fields: prevState.currentReportModel.custom_fields.map(
          (field, id) => {
            const returnField = { ...field };
            if (id === index) {
              switch (propertyName) {
                case 'title':
                  returnField.title = value;
                  if (this.state.isNew) {
                    returnField.name = this.createName(value);
                  }
                  break;
                case 'type':
                  returnField.type = value;
                  break;
                case 'enum' :
                  returnField.enum = value;
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
        fieldName: Object.values(prevState.formWarnings.fieldTitle).map(
          (value, id) => {
            return propertyName === 'title' && value && id === index
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
    const custom_fields = this.state.currentReportModel
      .custom_fields;
    custom_fields.push(defaultCustomField);
    this.setState((prevState) => ({
      currentReportModel: {
        ...prevState.currentReportModel,
        custom_fields,
      },
      formWarnings: {
        ...prevState.formWarnings,
        fields:
          prevState.currentReportModel.custom_fields.length > 0
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
        custom_fields: prevState.currentReportModel.custom_fields.filter(
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
        this.setState((prevState) => ({
          currentReportModel: response.data,
          isNew: false
        }));
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
      title: this.state.currentReportModel.title,
      name: this.state.currentReportModel.name,
      layer_id: this.state.currentReportModel.layer_id,
      custom_fields: this.state.currentReportModel.custom_fields,
    };

    ReportModelApiService.create(data, this.source.token)
      .then((response) => {
        this.setState({
          id: response.data.id,
          title: response.data.title,
          name: response.data.name,
          layer_id: response.data.layer_id,
          custom_fields: response.data.custom_fields,
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
    if (this.state.currentReportModel.title === '') {
      formWarnings.title = 'Veuillez indiquer un titre';
      valid = false;
    }
    if (this.state.currentReportModel.name === '') {
      formWarnings.name = 'Veuillez indiquer un nom';
      valid = false;
    }
    if (this.state.currentReportModel.name != '' && this.state.currentReportModel.name.match(/[^a-z_0-9]/)) {
      formWarnings.name = 'Caractères autorisés : minuscules, chiffres et \'_\'.';
      valid = false;
    }
    if (this.state.currentReportModel.layer_id === '') {
      formWarnings.layer = 'Veuillez indiquer une couche';
      valid = false;
    }
    if (this.state.currentReportModel.custom_fields.length === 0) {
      formWarnings.fields = 'Veuillez ajouter au moins un champ';
      valid = false;
    }
    for (const f in this.state.currentReportModel.custom_fields) {
      if (this.state.currentReportModel.custom_fields[f].title === '') {
        formWarnings.fieldTitle[f] = 'obligatoire';
        valid = false;
      }
      if (this.state.currentReportModel.custom_fields[f].type === '') {
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
    const { currentReportModel, layers, formWarnings } = this.state;

    const options = layers.map(layer => this.layerOption(layer));

    return (
      <div>
        {currentReportModel && (
          <div className="edit-form">
            <h4>Modèle de rapport</h4>
            <form>
              <div className="form-group">
                <label htmlFor="title">Titre*</label>
                <span style={{ color: 'red', float: 'right' }}>
                  {formWarnings['title']}
                </span>
                <input
                  required
                  type="text"
                  className="form-control"
                  id="title"
                  value={currentReportModel.title}
                  onChange={(e) => this.onTitleChange(e)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="name">Nom*</label>
                <span style={{ color: 'red', float: 'right' }}>
                  {formWarnings['name']}
                </span>
                <input
                  required
                  type="text"
                  className="form-control"
                  id="name"
                  value={currentReportModel.name}
                  onChange={(e) => this.onNameChange(e)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="layer_id">Couche associée*</label>
                <span style={{ color: 'red', float: 'right' }}>
                  {formWarnings['layer']}
                </span>
                <Select
                  id="layer_id"
                  value={this.layerOption(currentReportModel.layer_id)}
                  onChange={(e) => this.onLayerChange(e)}
                  options={options}
                />
              </div>


              <label htmlFor="custom_fields">Champs de formulaire</label>
              <span style={{ color: 'red', float: 'right' }}>
                {formWarnings['fields']}
              </span>
              <div id="custom_fields" className="form-group">
                {currentReportModel.custom_fields.length !== 0 ? (
                  currentReportModel.custom_fields.map((field, index) => (
                    <div key={index} className="row">
                      <div className="col-4">
                        <label htmlFor="field_title">Libellé*</label>
                        <input
                          type="text"
                          aria-label='libelle'
                          className="form-control mb-2"
                          value={field.title}
                          id="field_title"
                          onChange={(e) => this.onFieldChange('title', e.target.value, index)}
                        />
                        {formWarnings['fieldTitle'] && (
                          <span style={{ color: 'red' }}>
                            {formWarnings['fieldTitle'][index]}
                          </span>
                        )}
                      </div>
                      <div className="col-4">
                        <label htmlFor="field_type">Type*</label>
                        <select
                          className="form-control mb-2"
                          aria-label='type'
                          value={field.type}
                          id="field_type"
                          onChange={(e) => this.onFieldChange('type', e.target.value, index)}
                        >
                          <option value=""></option>
                          <option value="string">texte</option>
                          <option value="enum">
                            liste déroulante
                          </option>
                          <option value="number">numérique</option>
                          <option value="boolean">booléen</option>
                          <option value="date">date</option>
                          <option value="file">photo</option>
                        </select>
                        {currentReportModel.custom_fields[index].type === "enum" && (
                          <TagsInput 
                            value={currentReportModel.custom_fields[index].enum} 
                            inputProps={{placeholder:'choix possibles'}}
                            onChange={(e) => this.onFieldChange('enum', e, index)}
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
                          aria-label='requis'
                          type="checkbox"
                          aria-label='field_required'
                          checked={field.required}
                          id="field_required"
                          onChange={(e) =>
                            this.onFieldChange('required', e.target.checked, index)
                          }
                        />
                      </div>
                      <div className="col-1">
                        <button
                          className="btn btn-danger mt-4"
                          aria-label='delete field'
                          onClick={(e) => this.deleteField(index, e)}
                        >
                          <FaMinus />
                        </button>
                      </div>
                      <div className="col-1">
                        {index ===
                          currentReportModel.custom_fields.length - 1 && (
                          <button
                            type="submit"
                            className="btn btn-success mt-4"
                            aria-label='add a field'
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
                    type="submit"
                    className="btn btn-success"
                    aria-label='add a field'
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
