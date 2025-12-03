/**
 * Tests for utility functions
 * Tests pure functions for data transformation and formatting
 */
import { describe, it, expect } from 'vitest';
import { username, slug, getTotalScore, organizationColor } from '../../src/components/utils';
import { User, Application } from '../../src/components/types';

describe('Utility Functions', () => {
  describe('username', () => {
    it('returns full name when first and last name are provided', () => {
      const user: User = {
        id: 1,
        username: 'johndoe',
        first_name: 'John',
        last_name: 'Doe',
        organization: 'Test Org'
      };

      expect(username(user)).toBe('John Doe');
    });

    it('returns username when first or last name is missing', () => {
      const user: User = {
        id: 1,
        username: 'johndoe',
        first_name: '',
        last_name: 'Doe',
        organization: 'Test Org'
      };

      expect(username(user)).toBe('johndoe');
    });

    it('returns username when both names are empty', () => {
      const user: User = {
        id: 1,
        username: 'johndoe',
        first_name: '',
        last_name: '',
        organization: 'Test Org'
      };

      expect(username(user)).toBe('johndoe');
    });
  });

  describe('slug', () => {
    it('removes spaces from string', () => {
      expect(slug('Test Organization')).toBe('TestOrganization');
    });

    it('removes special characters and numbers from string', () => {
      // slug removes all non-alphabetic characters, including numbers
      expect(slug('Test-Org@123')).toBe('TestOrg');
    });

    it('preserves alphabetic characters', () => {
      expect(slug('TestOrg')).toBe('TestOrg');
    });

    it('handles empty string', () => {
      expect(slug('')).toBe('');
    });

    it('removes all non-alphabetic characters', () => {
      // slug removes everything except letters (no numbers, spaces, or special chars)
      expect(slug('Test & Co. (2024)')).toBe('TestCo');
    });
  });

  describe('getTotalScore', () => {
    it('calculates total score with multiplier', () => {
      const application: Application = {
        id: 1,
        name: 'Test',
        description: '',
        scores: [],
        comments: [],
        attachments: [],
        score: 3.5,
        scored: true,
        groupScores: {},
        scoresByOrganization: {},
        scoresByEvaluator: {},
        evaluating_organizations: []
      };

      // Score of 3.5 * multiplier of 4 = 14.0
      expect(getTotalScore(application)).toBe('14.0');
    });

    it('handles decimal scores correctly', () => {
      const application: Application = {
        id: 1,
        name: 'Test',
        description: '',
        scores: [],
        comments: [],
        attachments: [],
        score: 4.75,
        scored: true,
        groupScores: {},
        scoresByOrganization: {},
        scoresByEvaluator: {},
        evaluating_organizations: []
      };

      // Score of 4.75 * multiplier of 4 = 19.0
      expect(getTotalScore(application)).toBe('19.0');
    });

    it('returns null for null score', () => {
      const application: Application = {
        id: 1,
        name: 'Test',
        description: '',
        scores: [],
        comments: [],
        attachments: [],
        score: null as any,
        scored: false,
        groupScores: {},
        scoresByOrganization: {},
        scoresByEvaluator: {},
        evaluating_organizations: []
      };

      // getTotalScore returns null (not undefined) when score is null
      expect(getTotalScore(application)).toBeNull();
    });
  });

  describe('organizationColor', () => {
    it('returns consistent color for same organization', () => {
      const color1 = organizationColor('Test Org');
      const color2 = organizationColor('Test Org');

      expect(color1).toBe(color2);
    });

    it('returns hex color code', () => {
      const color = organizationColor('New Org');

      expect(color).toMatch(/^#[0-9A-F]{6}$/i);
    });

    it('assigns different colors to different organizations', () => {
      const color1 = organizationColor('Org A');
      const color2 = organizationColor('Org B');

      // Note: This might fail if colors wrap around, but unlikely with test data
      expect(color1).not.toBe(color2);
    });
  });
});
