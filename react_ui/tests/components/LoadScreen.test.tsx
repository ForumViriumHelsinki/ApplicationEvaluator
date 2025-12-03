/**
 * Tests for LoadScreen component
 * Tests basic rendering of the loading screen with logo and title
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadScreen from '../../src/components/LoadScreen';

describe('LoadScreen', () => {
  it('renders the application title', () => {
    render(<LoadScreen />);
    expect(screen.getByText('FVH Application Evaluator')).toBeInTheDocument();
  });

  it('renders the logo image', () => {
    render(<LoadScreen />);
    const logo = screen.getByAltText('logo');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'images/CommuniCity-logo-blue.png');
  });

  it('has correct container structure', () => {
    const { container } = render(<LoadScreen />);
    expect(container.querySelector('.container')).toBeInTheDocument();
    expect(container.querySelector('.jumbotron')).toBeInTheDocument();
  });
});
