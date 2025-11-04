import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('COC-D Switcher App', () => {
  test('renders main heading', () => {
    render(<App />);
    const heading = screen.getByText(/COC-D Switcher/i);
    expect(heading).toBeInTheDocument();
  });

  test('renders dashboard heading', () => {
    render(<App />);
    const dashboardHeading = screen.getByText(/Dashboard/i);
    expect(dashboardHeading).toBeInTheDocument();
  });

  test('displays ready message', () => {
    render(<App />);
    const readyMessage = screen.getByText(/Application is ready for development/i);
    expect(readyMessage).toBeInTheDocument();
  });
});