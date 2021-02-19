import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

test('renders app title', () => {
  render(<App />);
  const title = screen.getByText(/drealcorse-reports/i);
  expect(title).toBeInTheDocument();
});

test('init App with list of one Report Model', async () => {
  render(<App />);
  expect(screen.queryByText('TestModel')).toBeNull();
  await waitFor(() => {
    expect(screen.queryByText('TestModel')).toBeInTheDocument();
  });
});
