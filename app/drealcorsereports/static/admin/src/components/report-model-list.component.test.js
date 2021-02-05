import { render, screen, waitFor } from '@testing-library/react';
import ReportModelList from './report-model-list.component';

describe('Test Report Model List Component', () => {
  test('init component with list of one Report Model', async () => {
    render(<ReportModelList />);
    //check if TestModel is not present after rendering
    expect(screen.queryByText('TestModel')).toBeNull();
    // //check if TestModel is queried from API
    await waitFor(() => {
      expect(screen.queryByText('TestModel')).toBeInTheDocument();
    });
  });
});
