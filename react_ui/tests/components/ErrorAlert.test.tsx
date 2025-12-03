/**
 * Tests for ErrorAlert component
 * Tests conditional rendering and error message display
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ErrorAlert from '../../src/util_components/bootstrap/ErrorAlert';

describe('ErrorAlert', () => {
  it('displays error message when status is true', () => {
    render(<ErrorAlert status={true} message="Something went wrong" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('alert-danger');
  });

  it('does not display when status is false', () => {
    const { container } = render(<ErrorAlert status={false} message="Error message" />);
    expect(screen.queryByText('Error message')).not.toBeInTheDocument();
    expect(container.querySelector('.alert')).not.toBeInTheDocument();
  });

  it('does not display when status is undefined', () => {
    const { container } = render(<ErrorAlert message="Error message" />);
    expect(screen.queryByText('Error message')).not.toBeInTheDocument();
    expect(container.querySelector('.alert')).not.toBeInTheDocument();
  });

  it('renders with correct ARIA role', () => {
    render(<ErrorAlert status={true} message="Test error" />);
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
  });
});
