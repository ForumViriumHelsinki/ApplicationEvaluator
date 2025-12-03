/**
 * Example test file demonstrating Vitest with React Testing Library
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('Example Tests', () => {
  it('renders without crashing', () => {
    render(<div data-testid="test-element">Hello World</div>);
    expect(screen.getByTestId('test-element')).toBeInTheDocument();
  });

  it('displays correct text', () => {
    render(<div>Test Content</div>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});
