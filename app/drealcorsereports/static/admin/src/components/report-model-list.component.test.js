import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ReportModelList from './report-model-list.component';

const propsReportModelsMock = [
  {
    created_at: '2021-02-03T10:05:28.014020+00:00',
    updated_at: '2021-02-03T10:05:28.014034+00:00',
    custom_field_schema: [
      {
        name: 'TestField',
        type: 'string',
        required: false,
      },
    ],
    name: 'TestModel',
    updated_by: 'testuserid',
    layer_id: 'TestLayer',
    created_by: 'testuserid',
    id: 'cc0e41cc-5e71-4ba8-b9ba-fc8606ac2105',
  },
];

const editReportModelMock = jest.fn();

describe('Test Report Model List Component', () => {
  test('init component with list of one Report Model', async () => {
    render(
      <ReportModelList
        reportModels={propsReportModelsMock}
        editReportModel={editReportModelMock}
      />
    );
    expect(screen.queryByText('TestModel')).toBeInTheDocument();
    expect(screen.queryByText('TestLayer')).toBeInTheDocument();
    expect(screen.queryAllByText('testuserid')).toHaveLength(2);
  });

  test('call editReportModelMock when clicking button', async () => {
    render(
      <ReportModelList
        reportModels={propsReportModelsMock}
        editReportModel={editReportModelMock}
      />
    );
    fireEvent.click(screen.getAllByRole('button')[1], {
      target: { type: 'submit' },
    });
    await waitFor(() => {
      expect(editReportModelMock).toHaveBeenCalledTimes(1);
    });
  });
});
