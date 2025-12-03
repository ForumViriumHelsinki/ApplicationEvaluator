/**
 * Tests for CriterionScore component
 * Tests score input, display, and user interactions
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CriterionScore from '../../src/components/CriterionScore';
import { AppContext, Application, Criterion, User } from '../../src/components/types';

describe('CriterionScore', () => {
  const mockUser: User = {
    id: 1,
    username: 'testuser',
    first_name: 'Test',
    last_name: 'User',
    organization: 'Test Org'
  };

  const mockCriterion: Criterion = {
    id: 1,
    name: 'Quality',
    group: 1,
    weight: 1.0
  };

  const mockApplication: Application = {
    id: 1,
    name: 'Test App',
    description: '',
    scores: [],
    comments: [],
    attachments: [],
    score: 0,
    scored: false,
    groupScores: {},
    scoresByOrganization: {},
    scoresByEvaluator: {},
    evaluating_organizations: []
  };

  const mockContext = {
    user: mockUser,
    reloadApplication: vi.fn(),
    request: vi.fn().mockResolvedValue({ status: 200 }),
    updateApplication: vi.fn(),
    loadRounds: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays criterion name', () => {
    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={mockApplication} />
      </AppContext.Provider>
    );

    expect(screen.getByText(/Quality/)).toBeInTheDocument();
  });

  it('shows input field when no score exists and not readonly', () => {
    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={mockApplication} />
      </AppContext.Provider>
    );

    const input = screen.getByRole('spinbutton');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
    expect(input).toHaveAttribute('min', '0');
    expect(input).toHaveAttribute('max', '5');
    expect(input).toHaveAttribute('step', '0.5');
  });

  it('does not show input field in readonly mode', () => {
    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={mockApplication} readOnly={true} />
      </AppContext.Provider>
    );

    expect(screen.queryByRole('spinbutton')).not.toBeInTheDocument();
  });

  it('displays existing score with evaluator name', () => {
    const applicationWithScore: Application = {
      ...mockApplication,
      scores: [{
        id: 1,
        score: 4.5,
        evaluator: mockUser,
        criterion: mockCriterion.id
      }]
    };

    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={applicationWithScore} showScores={true} />
      </AppContext.Provider>
    );

    expect(screen.getByText(/4.5/)).toBeInTheDocument();
    expect(screen.getByText(/by Test User/)).toBeInTheDocument();
  });

  it('shows save button when input is changed', async () => {
    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={mockApplication} />
      </AppContext.Provider>
    );

    const input = screen.getByRole('spinbutton');
    await userEvent.type(input, '3.5');

    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('hides scores from other evaluators when showScores is false', () => {
    const otherUser: User = {
      id: 2,
      username: 'otheruser',
      first_name: 'Other',
      last_name: 'User',
      organization: 'Other Org'
    };

    const applicationWithScore: Application = {
      ...mockApplication,
      scores: [{
        id: 1,
        score: 4.5,
        evaluator: otherUser,
        criterion: mockCriterion.id
      }]
    };

    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={applicationWithScore} showScores={false} />
      </AppContext.Provider>
    );

    // Score value should be hidden (shown as '?')
    expect(screen.getByText('?')).toBeInTheDocument();
    expect(screen.queryByText('4.5')).not.toBeInTheDocument();
  });

  it('always shows own scores even when showScores is false', () => {
    const applicationWithScore: Application = {
      ...mockApplication,
      scores: [{
        id: 1,
        score: 4.5,
        evaluator: mockUser,
        criterion: mockCriterion.id
      }]
    };

    render(
      <AppContext.Provider value={mockContext}>
        <CriterionScore criterion={mockCriterion} application={applicationWithScore} showScores={false} />
      </AppContext.Provider>
    );

    // Own score should always be visible
    expect(screen.getByText(/4.5/)).toBeInTheDocument();
  });
});
