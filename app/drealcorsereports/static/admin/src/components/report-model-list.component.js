import React, { Component } from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import { FaPen } from 'react-icons/fa';

export default class ReportModelList extends Component {
  render() {
    const reportModels = this.props.reportModels;
    const formatDate = (dateStringISO) => {
      const timestamp = Date.parse(dateStringISO);
      const date = new Date(timestamp);
      const dateStringFR = date.toLocaleString('fr-FR');
      return dateStringFR;
    };
    const columns = [
      {
        dataField: 'name',
        text: 'Titre',
        sort: true,
      },
      {
        dataField: 'layer_id',
        text: 'Couche',
        sort: true,
      },
      {
        dataField: 'created_at',
        text: 'Créé le',
        sort: true,
        formatter: (cell, row) => {
          return formatDate(cell);
        },
      },
      {
        dataField: 'created_by',
        text: 'Créé par',
        sort: true,
      },
      {
        dataField: 'updated_at',
        text: 'Mise à jour le',
        sort: true,
        formatter: (cell, row) => {
          return formatDate(cell);
        },
      },
      {
        dataField: 'updated_by',
        text: 'Mise à jour par',
        sort: true,
      },
      {
        dataField: 'edit_button',
        text: '',
        isDummyField: true,
        align: 'center',
        formatter: (cell, row) => (
          <button
            onClick={() => this.props.editReportModel(row)}
            className="btn btn-secondary"
          >
            <FaPen />
          </button>
        ),
      },
    ];

    return (
      <div className="col-md-12">
        <h4>
          Liste des modèles de rapport
          <button
            onClick={() => this.props.addReportModel()}
            className="btn btn-warning float-right mb-3"
          >
            Ajouter un modèle
          </button>
        </h4>

        <BootstrapTable
          keyField="id"
          bootstrap4={true}
          hover={true}
          bordered={false}
          data={reportModels}
          columns={columns}
        />
      </div>
    );
  }
}
