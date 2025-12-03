/**
 * Tests for ApplicationRounds component
 * Tests loading states, error handling, and application round display
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ApplicationRounds from '../../src/components/ApplicationRounds';
import { User, ApplicationRound } from '../../src/components/types';

describe('ApplicationRounds', () => {
  const mockUser: User = {
    id: 1,
    username: 'testuser',
    first_name: 'Test',
    last_name: 'User',
    organization: 'Test Org'
  };

  const mockApplicationRound: ApplicationRound = {
    id: 1,
    name: 'Test Round',
    description: 'Test description',
    applications: [],
    criteria: [],
    criterion_groups: [],
    attachments: [],
    submitted_organizations: []
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays empty state when no applications exist', async () => {
    const mockRequest = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => []
    });

    render(<ApplicationRounds user={mockUser} request={mockRequest} />);

    await waitFor(() => {
      expect(screen.getByText('No applications currently awaiting evaluation.')).toBeInTheDocument();
    });
  });

  it('displays error message when request fails', async () => {
    const mockRequest = vi.fn().mockResolvedValue({
      status: 500
    });

    render(<ApplicationRounds user={mockUser} request={mockRequest} />);

    await waitFor(() => {
      expect(screen.getByText(/Error fetching applications/)).toBeInTheDocument();
    });
  });

  it('calls request function with correct URL on mount', () => {
    const mockRequest = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => []
    });

    render(<ApplicationRounds user={mockUser} request={mockRequest} />);

    expect(mockRequest).toHaveBeenCalledTimes(1);
    expect(mockRequest).toHaveBeenCalledWith('/rest/application_rounds/');
  });

  it('renders application rounds when data is loaded', async () => {
    const mockRequest = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => [{
        ...mockApplicationRound,
        applications: [{
          id: 1,
          name: 'Test Application',
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
        }]
      }]
    });

    render(<ApplicationRounds user={mockUser} request={mockRequest} />);

    await waitFor(() => {
      expect(screen.getByText('Test Round')).toBeInTheDocument();
    });
  });

  it('returns null while loading (before data arrives)', () => {
    const mockRequest = vi.fn().mockImplementation(() => new Promise(() => {}));
    const { container } = render(<ApplicationRounds user={mockUser} request={mockRequest} />);

    // Component returns null while loading, so container should be empty
    expect(container.firstChild).toBeNull();
  });
});
