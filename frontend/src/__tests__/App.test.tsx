import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

describe('COC-D Switcher App', () => {
  test('renders main heading', () => {
    render(<App />);
    const heading = screen.getByText(/COC-D Switcher/i);
    expect(heading).toBeInTheDocument();
  });

  test('create job button works', async () => {
    render(<App />);
    const button = screen.getByText(/Create New Job/i);
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(button).toHaveTextContent(/Creating.../i);
    });
  });

  test('displays validation errors', () => {
    const mockErrors = [
      { code: 'SERIAL_COUNT_MISMATCH', message: 'Serial count mismatch', where: 'serials' }
    ];
    
    // Test validation panel with errors
    // Implementation depends on your component structure
  });
});