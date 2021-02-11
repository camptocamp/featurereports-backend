import React, { Component } from 'react';
import BootstrapTable from 'react-bootstrap-table-next';

export default class ReportModelList extends Component {
  render() {
    const reportModels = this.props.reportModels;

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
        formatter: (cell, row) => (
          <button
            onClick={() => this.props.editReportModel(row)}
            className="btn btn-warning"
          >
            Modifier
          </button>
        ),
      },
    ];

    return (
      <div className="list row">
        <div className="col-md-12">
          <BootstrapTable
            keyField="id"
            bootstrap4={true}
            hover={true}
            data={reportModels}
            columns={columns}
          />
        </div>
      </div>
    );
  }
}
