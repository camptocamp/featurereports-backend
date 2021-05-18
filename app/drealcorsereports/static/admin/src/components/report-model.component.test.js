import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ReportModel from './report-model.component';

const reportModelMock = {
  id: null,
  title: '',
  name: '',
  layer_id: '',
  custom_fields: [],
  created_at: '',
  created_by: '',
  updated_at: '',
  updated_by: '',
};

const refreshListMock = jest.fn();

describe('Test Report Model Component', () => {
  test('init component without report model for adding', async () => {
    render(
      <ReportModel
        key="add"
        currentReportModel={reportModelMock}
        onReportModelChange={refreshListMock}
      />
    );
    //check if Test values are not present after rendering
    expect(screen.queryByDisplayValue(/Test/)).toBeNull();
    //check if Test values are not queried from API
    expect(await screen.queryByDisplayValue('TestModel')).toBeNull();
    expect(await screen.queryByDisplayValue('TestLayer')).toBeNull();
    expect(await screen.queryByDisplayValue('TestField')).toBeNull();
  });

  test('adds ReportModel and calls onReportModelChange', async () => {
    render(
      <ReportModel
        key="add"
        currentReportModel={reportModelMock}
        onReportModelChange={refreshListMock}
      />
    );
    //fill form with valid data
    fireEvent.click(screen.getAllByRole('button')[0], {
      target: { type: 'submit' },
    });
    userEvent.type(screen.getByLabelText(/Titre/), 'Model Name');
    userEvent.type(screen.getByText(/Couche/), 'Layer Name');
    userEvent.type(screen.getByLabelText(/Libellé/), 'Field Name');
    userEvent.selectOptions(screen.getByLabelText(/Type/), ['texte']);
    //workaround to wait for user events
    setTimeout(async () => {
      //confirm window alert
      window.confirm = jest.fn(() => true);
      //trigger add
      fireEvent.click(screen.getByText(/Sauvegarder/), {
        target: { type: 'submit' },
      });
      //wait for component callback to be called
      await waitFor(() => {
        expect(refreshListMock).toHaveBeenCalledTimes(1);
      });
    }, 1000);
  });

  test('init component with report model for editing', async () => {
    //set id to query report model from msw api
    reportModelMock.id = 1;
    render(
      <ReportModel
        key="edit"
        currentReportModel={reportModelMock}
        onReportModelChange={refreshListMock}
      />
    );
    //check if Test values are not present after rendering
    expect(screen.queryByDisplayValue(/Test/)).toBeNull();
    //check if Test values are present after querying API
    expect(await screen.findByDisplayValue('TestModel')).toBeInTheDocument();
    expect(await screen.findByText('TestLayer')).toBeInTheDocument();
    expect(await screen.findByDisplayValue('TestField')).toBeInTheDocument();
    expect(await screen.findByLabelText('field_required').checked);
    //check presence of dropdown element and its tags
    expect(await screen.findByDisplayValue('TestField-TestTags')).toBeInTheDocument();
    expect(await screen.findByText('firstChoice')).toBeInTheDocument();
    expect(await screen.findByText('secondChoice')).toBeInTheDocument();
  });

  test('updates ReportModel and calls onReportModelChange', async () => {
    reportModelMock.id = 1;
    render(
      <ReportModel
        key="edit"
        currentReportModel={reportModelMock}
        onReportModelChange={refreshListMock}
      />
    );
    //wait for ReportModel with valid data to be queried
    expect(await screen.findByDisplayValue('TestModel')).toBeInTheDocument();
    //confirm window alert
    window.confirm = jest.fn(() => true);
    //add a field
    screen.getByLabelText(/add a field/).click();
    userEvent.type(screen.getAllByLabelText('libelle')[2], 'new Field Name');
    userEvent.selectOptions(screen.getAllByLabelText('type')[2], ['string']);
    //trigger update
    fireEvent.click(screen.getByText(/Sauvegarder/), {
      target: { type: 'submit' },
    });
    //wait for component callback to be called
    await waitFor(() => {
      expect(refreshListMock).toHaveBeenCalledTimes(1);
    });
  });

  test('deletes ReportModel and calls onReportModelChange', async () => {
    reportModelMock.id = 1;
    render(
      <ReportModel
        key="edit"
        currentReportModel={reportModelMock}
        onReportModelChange={refreshListMock}
      />
    );
    //wait for ReportModel with valid data to be queried
    expect(await screen.findByDisplayValue('TestModel')).toBeInTheDocument();
    //confirm window alert
    window.confirm = jest.fn(() => true);
    //trigger delete
    fireEvent.click(screen.getByText(/Supprimer/), {
      target: { type: 'submit' },
    });
    //wait for component callback to be called
    await waitFor(() => {
      expect(refreshListMock).toHaveBeenCalledTimes(1);
    });
  });
});
